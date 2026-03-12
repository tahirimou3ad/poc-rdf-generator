# POC : Générateur de Graphe de Connaissances RDF

> **Projet de Preuve de Concept (POC)** : Transformation automatique de textes en langage naturel vers un graphe de connaissances RDF structuré.

---

## Objectifs

Ce projet implémente un pipeline hybride combinant :

1.  **Approche Symbolique** : Analyse syntaxique et extraction d'entités (SpaCy).
2.  **Approche Neuronale** : Consolidation sémantique via LLM (Ollama/Llama3).
3.  **Validation Humaine** : Interface interactive pour valider les résultats.

---

## Installation et Lancement

### 1. Prérequis

Assurez-vous d'avoir installé sur votre machine :

- Python 3.10 ou supérieur.
- [Ollama](https://ollama.com/) pour le modèle IA.

### 2. Installation des dépendances

Clonez le dépôt et installez les librairies nécessaires :

```bash
git clone https://github.com/tahirimou3ad/poc-rdf-generator
cd poc-rdf-generator

# Création de l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances Python
pip install -r requirements.txt

# Téléchargement du modèle linguistique SpaCy
python -m spacy download fr_core_news_lg

# Téléchargement du modèle IA (Llama3 ou Phi3)
ollama pull llama3
```

### 3. Lancement de l'application

```bash
# Lancer le serveur IA (si non actif)
ollama serve &

# Lancer l'interface web
streamlit run app.py
```
