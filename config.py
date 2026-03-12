import os

class Config:
    # Section 3.1 & 3.2 : Configuration
    DEFAULT_LANG = "fr"
    
    # Section 4.3 : Modèles SpaCy (Version LARGE pour meilleure précision NER)
    SPACY_MODELS = {
        "en": "en_core_web_lg",
        "fr": "fr_core_news_lg"
    }
    
    # Section 6.2 : Seuils de décision automatisée
    THRESHOLD_AUTO_VALIDATE = 0.85
    THRESHOLD_HUMAN_REVIEW = 0.70
    
    # Section 6.2 : Paramètres de confiance combinée
    LLM_WEIGHT = 0.6   # Beta
    SYNTAX_WEIGHT = 0.4 # Alpha
    
    # Section 6.2 : Technologie LLM (Llama3 installé via Ollama)
    LLM_PROVIDER = "ollama"
    LLM_MODEL = "llama3"
