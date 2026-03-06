import logging
from htag import Tag, ChromeApp, State

logging.basicConfig(level=logging.INFO)

class DemoApp(Tag.App):
    def init(self):
        # 1. État Réactif (State)
        # On déclare une variable réactive.
        self.compteur = State(0)

        # 2. Syntaxe "with" (Context Manager)
        # Permet d'imbriquer visuellement les balises sans avoir à faire de "self <= ..." à chaque ligne.
        with Tag.div(_style="font-family: sans-serif; padding: 20px; max-width: 500px; margin: auto;"):
            
            Tag.h2("🛠 Démo des Nouvelles Fonctionnalités", _style="color: #2c3e50;")
            
            # --- Cas 1 : Le State Réactif ---
            with Tag.div(_style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; margin-bottom: 20px; background: #f9f9f9;"):
                Tag.h3("1. L'État Réactif (State)", _style="margin-top: 0;")
                Tag.p("Le texte ci-dessous se met à jour TOUT SEUL quand la valeur change.")
                
                # La fonction lambda permet à htag2 de s'abonner automatiquement au "State".
                Tag.div(lambda: f"👉 Valeur actuelle du compteur : {self.compteur.value}", _style="font-size: 1.2em; font-weight: bold; margin-bottom: 15px; color: #e74c3c;")
                
                # Le bouton modifie seulement la variable, pas l'interface
                Tag.button("Incrémenter le State", _onclick=self.incrementer_state, _style="padding: 8px 12px; cursor: pointer;")
            
            # --- Cas 2 : La propriété .text ---
            with Tag.div(_style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; background: #f9f9f9;"):
                Tag.h3("2. La propriété .text", _style="margin-top: 0;")
                Tag.p("Pour les remplacements simples et rapides de texte sans dépendre d'un State global.")
                
                # On garde une référence locale pour pouvoir modifier son texte plus tard
                self.message_label = Tag.div("Texte initial", _style="font-style: italic; margin-bottom: 15px;")
                
                # Le bouton déclenche un événement qui modifie la cible de façon impérative
                Tag.button("Modifier le texte", _onclick=self.changer_texte, _style="padding: 8px 12px; cursor: pointer;")

    def incrementer_state(self, e):
        # On modifie PUREMENT la logique métier. 
        # htag2 détecte ce changement et rafraîchit l'UI correspondante instantanément.
        self.compteur.value += 1

    def changer_texte(self, e):
        # Sans le '.text', on aurait dû faire :
        # self.message_label.clear()
        # self.message_label.add("Nouveau texte !")
        
        # Maintenant, on écrase directement le contenu grâce au raccourci .text :
        self.message_label.text = "✅ Le texte a été remplacé proprement via .text !"

if __name__ == "__main__":
    # Lancement de l'application
    ChromeApp(DemoApp, width=800, height=600).run()
