POC : Générateur de Graphe de Connaissances RDF
Ce projet est une preuve de concept (POC) permettant de transformer un texte en langage naturel en un graphe de connaissances RDF structuré. Il combine des approches symboliques (NLP), neuronales (LLM) et une validation humaine interactive.

- Fonctionnalités
Extraction d'entités nommées (NER) avec support de vocabulaire contrôlé.
Extraction de relations.
Consolidation sémantique par LLM.
Calcul de confiance hybride (Syntaxique + LLM).
Validation humaine interactive.
Export au format RDF (Turtle).

- Installation
Prérequis : Python 3.10+ et Ollama.
Cloner le dépôt :
git clone https://github.com/tahirimou3ad/poc-rdf-generator
cd poc-rdf-generator
Environnement virtuel :
python3 -m venv venv
source venv/bin/activate
Dépendances Python :
pip install -r requirements.txt
python -m spacy download fr_core_news_lg
Modèle IA (Llama3 ou Phi3) :
ollama pull llama3

- Utilisation
Lancer le serveur Ollama (si non lancé) :
ollama serve &
Lancer l'application :
streamlit run app.py
Ouvrir l'interface dans votre navigateur (généralement http://localhost:8501).

- Structure du Projet
app.py : Point d'entrée principal et interface Streamlit.
nlp_processor.py : Module de prétraitement et NER (SpaCy).
relation_extractor.py : Module d'extraction de relations (Syntaxe + LLM).
llm_service.py : Interface avec l'API Ollama.
rdf_builder.py : Génération du graphe RDF.
config.py : Configuration globale (seuils, modèles).

-  Logique de Calcul
La confiance finale d'une relation est calculée ainsi :C_combined = (0.4 * C_syntax) + (0.6 * C_llm)

C_syntax : Basé sur la proximité textuelle.
C_llm : Basé sur la cohérence de la réponse du LLM.
