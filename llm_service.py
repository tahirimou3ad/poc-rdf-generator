import ollama
from config import Config

class LLMService:
    def __init__(self):
        self.model = Config.LLM_MODEL
        print(f"--- Service LLM initialisé (Modèle : {self.model}) ---")

    def generate(self, prompt: str) -> str:
        """
        Section 6.2 : Consolidation sémantique par LLM.
        Transforme une relation syntaxique en relation sémantique stable.
        """
        try:
            response = ollama.chat(model=self.model, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Erreur LLM : {e}")
            return "erreur_relation"

    def augment_entity_type(self, entity_label: str, context: str) -> str:
        """
        Section 7.3 : Augmentation des entités (Inférence de types conceptuels).
        """
        prompt = (
            f"Contexte : '{context}'. "
            f"Quel est le type conceptuel RDF (ex: Organization, Person, Product) de l'entité '{entity_label}' ? "
            f"Réponds par un seul mot."
        )
        return self.generate(prompt)
