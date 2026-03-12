import spacy
from typing import List, Dict
from config import Config

class RelationExtractor:
    
    def _get_text_path(self, doc, start_token, end_token):
        """
        Trouve le chemin de mots le plus court entre deux tokens dans l'arbre syntaxique.
        Renvoie le texte des mots sur le chemin.
        """
        # Trouver le plus petit ancêtre commun
        ancestor = start_token
        path_start = []
        while ancestor != ancestor.head:
            path_start.append(ancestor)
            if ancestor.is_ancestor(end_token):
                break
            ancestor = ancestor.head
            
        path_end = []
        temp = end_token
        while temp != ancestor:
            path_end.append(temp)
            temp = temp.head
            
        # On reconstruit le chemin : Start -> Ancestor <- End
        tokens_on_path = path_start + [ancestor] + path_end[::-1]
        
        # Filtrer pour garder les mots importants (Verbes, Noms, Adjectifs, Prépositions)
        # et ignorer les déterminants (le, la, the) qui gênent souvent la lisibilité
        filtered_tokens = [
            t for t in tokens_on_path 
            if t.pos_ in ("VERB", "NOUN", "ADJ", "ADP", "AUX") and not t.is_stop
        ]
        
        # Si le chemin est vide, on prend les lemmes des tokens intermédiaires
        if not filtered_tokens:
             filtered_tokens = [t for t in tokens_on_path if t.pos_ != "PUNCT"]

        # Cas spécial : le verbe est 'être' (be/est) -> on garde le nom/adjectif qui suit
        # Ex: "Macron est président" -> on veut "est président"
        
        return " ".join([t.lemma_ for t in filtered_tokens if t.dep_ != "punct"])

    def extract_syntactic_relations(self, doc, entities: List[Dict]) -> List[Dict]:
        relations = []
        
        # Créer un mapping Token -> Entité
        token_to_ent = {}
        for ent in entities:
            for token in doc:
                if token.idx >= ent['start'] and token.idx < ent['end']:
                    token_to_ent[token] = ent

        # Trouver les paires d'entités dans la même phrase
        seen_pairs = set()
        
        # Pour chaque phrase
        for sent in doc.sents:
            # Récupérer les entités dans cette phrase
            ents_in_sent = [token_to_ent[t] for t in sent if t in token_to_ent]
            # Dédoublonner (une entité peut couvrir plusieurs tokens)
            unique_ents = {e['id']: e for e in ents_in_sent}.values()
            
            list_ents = list(unique_ents)
            
            # Pour chaque paire possible
            for i in range(len(list_ents)):
                for j in range(i + 1, len(list_ents)):
                    ent_a = list_ents[i]
                    ent_b = list_ents[j]
                    
                    # Trouver un token représentatif pour chaque entité (souvent la 'head')
                    # On prend le token 'head' de l'entité si possible
                    head_a = None
                    head_b = None
                    
                    # Trouver les heads syntaxiques des entités
                    for t in sent:
                        if t in token_to_ent and token_to_ent[t]['id'] == ent_a['id']:
                            # On veut le token qui 'gouverne' l'entité dans la phrase
                            if t.head.pos_ != "DET": 
                                head_a = t
                        if t in token_to_ent and token_to_ent[t]['id'] == ent_b['id']:
                            if t.head.pos_ != "DET":
                                head_b = t
                                
                    if not head_a or not head_b:
                        continue
                        
                    pair_id = tuple(sorted((ent_a['id'], ent_b['id'])))
                    if pair_id in seen_pairs:
                        continue
                    seen_pairs.add(pair_id)
                    
                    # Extraire le chemin textuel
                    relation_text = self._get_text_path(doc, head_a, head_b)
                    
                    # Nettoyage simple
                    relation_text = relation_text.replace("_", " ").strip()
                    
                    # Calcul de confiance (plus le chemin est court, plus c'est fiable)
                    dist = abs(head_a.i - head_b.i)
                    confidence = max(0.4, 1.0 - (dist * 0.02))

                    relations.append({
                        "subject": ent_a,
                        "predicate_raw": relation_text,
                        "object": ent_b,
                        "c_syntax": confidence,
                        "type": "syntactic_path"
                    })
                    
        return relations

    def consolidate_with_llm(self, relations: List[Dict], llm_service) -> List[Dict]:
        for rel in relations:
            if rel['c_syntax'] >= 0.4: 
                # Prompt amélioré pour le LLM
                prompt = (
                    f"Voici une relation brute extraite d'un texte : "
                    f"'{rel['subject']['label']}' -> '{rel['predicate_raw']}' -> '{rel['object']['label']}'. "
                    f"Propose une propriété RDF sémantique propre et concise qui résume cette relation "
                    f"(ex: 'est le président de', 'a fabriqué', 'est situé en'). "
                    f"Réponds uniquement par la propriété."
                )
                
                llm_response = llm_service.generate(prompt)
                
                # Nettoyage
                rel['predicate_clean'] = llm_response.replace('"', '').strip()
                rel['c_llm'] = 0.9 
                rel['c_combined'] = (Config.SYNTAX_WEIGHT * rel['c_syntax']) + (Config.LLM_WEIGHT * rel['c_llm'])
                
                if rel['c_combined'] >= Config.THRESHOLD_AUTO_VALIDATE:
                    rel['status'] = "auto_validated"
                else:
                    rel['status'] = "needs_review"
            else:
                rel['status'] = "rejected_low_syntax"
                
        return relations
