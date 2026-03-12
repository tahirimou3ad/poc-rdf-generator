import spacy
from typing import List, Dict, Any
from config import Config

class NLPProcessor:
    def __init__(self, language: str = "fr"):
        model_name = Config.SPACY_MODELS.get(language, "en_core_web_lg")
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise OSError(f"Modèle {model_name} manquant. Lancez: python -m spacy download {model_name}")

    def process(self, text: str, user_vocab: List[str] = None) -> Dict[str, Any]:
        doc = self.nlp(text)
        
        sentences = [{"text": sent.text, "start": sent.start_char, "end": sent.end_char} for sent in doc.sents]

        # Section 5.2 : Extraction NER Standard
        entities = []
        for ent in doc.ents:
            entities.append({
                "id": f"ent_{ent.start}_{ent.end}",
                "label": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "source": "spacy_ner"
            })

        # AMÉLIORATION : Fallback sur les Noms (Noun Chunks) si aucune entité NER détectée
        # Cela permet au graphe de fonctionner même avec des phrases génériques
        if not entities:
            for chunk in doc.noun_chunks:
                # On filtre les déterminants (le, la, the) et les stops words
                if len(chunk.text) > 2: 
                    entities.append({
                        "id": f"ent_chunk_{chunk.start}_{chunk.end}",
                        "label": chunk.text,
                        "type": "NOUN_CHUNK",
                        "start": chunk.start_char,
                        "end": chunk.end_char,
                        "source": "syntax_fallback"
                    })

        # Section 5.2b : Vocabulaire contrôlé (prioritaire)
        if user_vocab:
            for phrase in user_vocab:
                start_idx = text.find(phrase)
                if start_idx != -1:
                    end_idx = start_idx + len(phrase)
                    if not any(e['start'] <= start_idx < e['end'] for e in entities):
                        entities.append({
                            "id": f"ent_user_{start_idx}",
                            "label": phrase,
                            "type": "USER_DEFINED",
                            "start": start_idx,
                            "end": end_idx,
                            "source": "user_vocab"
                        })

        return {"doc": doc, "sentences": sentences, "entities": entities}
