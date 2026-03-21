# Pistes d'évolution pour le framework htag v2

Suite à l'analyse du document de bonnes pratiques (`htag-development`), voici des propositions d'améliorations à apporter au cœur du framework htag (`htag/core.py` et `htag/runner.py`) pour pallier aux éventuels soucis rencontrés par les développeurs.

## 1. Problème des "Clicks fantômes" lors du rendu basé sur des Lambdas
**Le problème** : L'utilisation de rendus dynamiques via des lambdas (`Tag.div(lambda: ...)`) recrée de nouveaux objets `Tag` à chaque changement d'état. Ces composants ont alors de nouveaux identifiants internes (`id`). Si un utilisateur clique sur un ancien élément pendant qu'une mise à jour est en cours de réception, l'événement JS est envoyé avec un `id` qui n'existe plus côté serveur, provoquant des "ghost clicks" ou une absence de réponse.
**La solution : Les identifiants stables (Stable IDs/Keys)**
Tout comme les `keys` sous React, il faut que l'attribut `_id` fourni par le développeur puisse fixer l'identifiant interne de l'objet de façon permanente.
*Modification proposée dans `htag/core.py` :*
- Dans `GTag.__init__`, intercepter `kwargs.get("_id")` et l'affecter directement à `self.id` au lieu de générer `div-123456`.
- Dans `GTag._render_attrs`, n'ajouter l'attribut redondant `data-htag-id` que si le développeur force une mutation du dictionnaire `self["id"]` qui diffèrerait de l'id d'origine.
- **Bénéfice** : Les composants récréés via lambda conserveront l'ID défini. Les événements en retard cibleront correctement la nouvelle instance générée. L'exigence de "rendering persistant" pour la stabilité s'efface.

## 2. Lourdes syntaxes pour les Events asynchrones et Timers (ex: Toasts)
**Le problème** : Pour masquer un Toast sans bloquer un thread Python avec `asyncio.sleep`, le skill recommande de déléguer le timer à Javascript en envoyant le bout de code suivant : `t.call_js(f"setTimeout(() => htag_event('{t.id}', 'expire', {{}}), 5000)")`. L'interpolation string manuelle pour appeler l'API interne `htag_event` est rébarbative et source d'erreurs d'échappement potentiel.
**La solution : Interfaces d'évènements simplifiées**
Ajouter des helpers Pythoniques sur l'objet `GTag` :
1. `GTag.js_event(event_name: str, payload: dict = None) -> str` : Renvoie la bonne chaîne JS pour appeler un événement python sur le composant (génère `htag_event('tag-id', 'eventName', {data})`).
2. `GTag.call_timeout(delay_ms: int, js: str)` : Permet d'encapsuler n'importe quel script Javascript dans un `setTimeout` côté navigateur.
- **Bénéfice** : L'implémentation d'un toast s'écrit alors proprement : `self.call_timeout(5000, self.js_event('expire'))`

## 3. Accès facilité aux formulaires (`e["fieldname"]`)
**Note (Déjà résolu)** : Le document de skill mentionnait l'utilisation de `e["fieldname"]` comme raccourci pour  `e.value["fieldname"]` lors de la soumission de formulaires. 
*Analyse du code* : Il s'avère que cela **est déjà implémenté** au sein de la méthode `__getitem__` de la classe `Event` (dans `htag/runner.py`). Aucune modification n'est donc requise pour cette fonctionnalité.
