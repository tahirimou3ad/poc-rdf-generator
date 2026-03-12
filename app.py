import streamlit as st
import pandas as pd
from config import Config
from nlp_processor import NLPProcessor
from relation_extractor import RelationExtractor
from llm_service import LLMService
from rdf_builder import RDFBuilder

# Configuration
st.set_page_config(layout="wide", page_title="POC Knowledge Graph Generator")

# Session State
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'relations' not in st.session_state:
    st.session_state.relations = None
if 'entities_df' not in st.session_state:
    st.session_state.entities_df = None
if 'last_text' not in st.session_state:
    st.session_state.last_text = ""

def main():
    st.title("🧠 POC : Générateur de Graphe de Connaissances RDF")
    
    @st.cache_resource
    def load_nlp(lang): return NLPProcessor(lang)
    @st.cache_resource
    def load_llm(): return LLMService()

    nlp_proc = load_nlp("fr")
    llm_service = load_llm()

    # --- Sidebar ---
    st.sidebar.header("1. Configuration")
    language = st.sidebar.selectbox("Langue du texte", ["fr", "en"], index=0)
    automation_level = st.sidebar.radio("Niveau d'automatisation", ["Hybride", "Symbolique seul", "Enrichi par LLM"], index=0)
    debug_mode = st.sidebar.checkbox("Mode Debug (Voir les détails)", value=True) # Activé par défaut pour aider
    
    vocab_input = st.sidebar.text_area("Vocabulaire contrôlé", "Apple\niPhone")
    user_vocab = [v.strip() for v in vocab_input.split('\n') if v.strip()]

    # --- Main ---
    st.header("2. Texte d'entrée")
    default_text = "Apple a lancé l'iPhone 15 en 2023. Tim Cook est le PDG d'Apple."
    text_input = st.text_area("Entrez le texte :", default_text, height=150)

    # Reset si texte change
    if text_input != st.session_state.last_text:
        st.session_state.processed_data = None
        st.session_state.relations = None
        st.session_state.entities_df = None
        st.session_state.last_text = text_input

    if st.button("🚀 Lancer le Pipeline", type="primary"):
        if not text_input:
            st.warning("Veuillez entrer du texte.")
        else:
            with st.status("Analyse en cours...", expanded=True) as status:
                nlp_proc = load_nlp(language)
                
                # NLP
                data = nlp_proc.process(text_input, user_vocab)
                st.write(f"✅ Phrases : {len(data['sentences'])}")
                st.write(f"✅ Entités détectées : {len(data['entities'])}")
                
                # Relations
                extractor = RelationExtractor()
                raw_rel = extractor.extract_syntactic_relations(data['doc'], data['entities'])
                st.write(f"✅ Relations candidates : {len(raw_rel)}")
                
                # LLM
                if automation_level != "Symbolique seul" and raw_rel:
                    st.write("🔄 Consolidation LLM en cours...")
                    consolidated_rel = extractor.consolidate_with_llm(raw_rel, llm_service)
                else:
                    consolidated_rel = raw_rel
                    for r in consolidated_rel:
                        r['c_combined'] = r.get('c_syntax', 0)
                        r['status'] = "needs_review"
                
                # Enrichissement types
                if automation_level == "Enrichi par LLM":
                     for ent in data['entities']:
                        ent['inferred_type'] = llm_service.augment_entity_type(ent['label'], text_input)

                st.session_state.processed_data = data
                st.session_state.relations = consolidated_rel
                st.session_state.entities_df = pd.DataFrame(data['entities'])
                status.update(label="Terminé.", state="complete")

    # --- Affichage ---
    if st.session_state.processed_data is not None:
        
        # Debug View
        if debug_mode:
            with st.expander("🐛 Debug : Analyse SpaCy détaillée"):
                doc = st.session_state.processed_data['doc']
                # Afficher les dépendances syntaxiques
                debug_data = []
                for token in doc:
                    debug_data.append({
                        "Texte": token.text,
                        "LEMME": token.lemma_,
                        "POS": token.pos_,
                        "Dépendance": token.dep_,
                        "Tête": token.head.text
                    })
                st.dataframe(pd.DataFrame(debug_data), use_container_width=True)

        st.subheader("Entités Extraites (Section 5)")
        df_ent = st.session_state.entities_df
        if df_ent.empty:
            st.error("❌ Aucune entité détectée ! Le graphe sera vide. Essayez d'ajouter des mots dans 'Vocabulaire contrôlé' ou utilisez des noms propres.")
        else:
            cols = [c for c in ['label', 'type', 'source'] if c in df_ent.columns]
            st.dataframe(df_ent[cols], use_container_width=True)

        st.subheader("Validation Humaine (Section 9)")
        if st.session_state.relations:
            df_rel_data = [{
                "Sujet": r['subject']['label'],
                "Relation": r.get('predicate_clean', r['predicate_raw']),
                "Objet": r['object']['label'],
                "Confiance": round(r.get('c_combined', 0), 2),
                "Statut": r.get('status'),
                "Valider": r.get('status') == 'needs_review'
            } for r in st.session_state.relations]
            
            df_rel = pd.DataFrame(df_rel_data)
            edited_df = st.data_editor(df_rel, column_config={"Valider": st.column_config.CheckboxColumn("Valider ?", default=False)}, hide_index=True, key="relation_editor")

            st.divider()
            if st.button("💾 Générer le Graphe RDF (Section 10)"):
                for i, r in enumerate(st.session_state.relations):
                    if r['status'] == 'needs_review':
                        if edited_df.iloc[i]['Valider']:
                            r['status'] = 'human_validated'
                        else:
                            r['status'] = 'human_rejected'

                builder = RDFBuilder()
                builder.build_graph(st.session_state.processed_data['entities'], st.session_state.relations)
                rdf_out = builder.serialize(format="turtle")
                
                st.subheader("Résultat RDF")
                st.code(rdf_out, language="turtle")
                st.download_button("Télécharger .ttl", rdf_out, "graph.ttl")
        else:
            st.warning("⚠️ Aucune relation trouvée. Vérifiez que les entités ont été détectées ci-dessus.")

if __name__ == "__main__":
    main()
