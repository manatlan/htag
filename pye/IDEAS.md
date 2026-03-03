# Idées d'évolutions pour pye (Serveur Htag Dynamique)

Ce document liste les évolutions conceptuelles potentielles pour rendre le serveur `pye` encore plus robuste ("Rock Solid") et adapté à des cas d'usage avancés en production, tout en essayant de préserver la philosophie "KISS" (Keep It Simple, Stupid).

### ~~1. La "vampirisation" des dossiers par l'App Htag~~ **(IMPLÉMENTÉ ✅)**
~~**Le problème :** Actuellement, l'app Htag "aspire" toutes les URL commençant par sa route (ex: `/folder/tutu2/`). Si une application contient un fichier statique comme `folder/tutu2/style.css`, Htag ne sait pas comment le servir.~~
~~**L'évolution :** Faire en sorte que le routeur intercepte les requêtes pour des fichiers statiques **avant** de transférer la requête à l'app Htag.~~
*   ~~*Avantage :* Permet de créer des apps autonomes qui contiennent leurs propres assets (images, css) au même niveau que le `__init__.py`.~~

### 2. Isolation totale de l'environnement d'exécution (Subprocess vs Import)
**Le problème :** Quand une App Htag est chargée, `importlib.import_module` est utilisé. Cela signifie que le code au niveau global (hors de la classe `App`) est exécuté **synchroniquement dans le processus principal d'Uvicorn**. Un script bogué (boucle infinie, `time.sleep`) gèlera tout le serveur `pye`. De plus, les apps partagent le même espace mémoire et peuvent interférer (ex: modification de `sys.path`).
**L'évolution :** "Spawner" chaque app `htag` dans son propre processus (comme on le fait pour les `.py` classiques) et faire en sorte que le serveur `pye` ne serve que de proxy HTTP/WebSocket vers ces processus enfants.
*   *Avantage :* Stabilité absolue. Un module vérolé ne crashe jamais le serveur hôte.

### ~~3. Gestion des WebSockets et de la mort d'une App~~ **(IMPLÉMENTÉ PARTIELLEMENT ✅)**
~~**Le problème :** Si on modifie le code source d'une app, Uvicorn rechargera le serveur entier, coupant brutalement toutes les websockets en cours pour tous les utilisateurs.~~
~~**L'évolution :** (Le Smart Reload gère cela désormais en ne rechargeant intelligemment que sur un accès `HTTP` natif).~~

### ~~4. La gestion du cache Python (`__pycache__`)~~ **(RÉSOLU VIA LE DEEP RELOAD ✅)**
~~**Le problème :** Avec `importlib.reload()`, Python gère le rechargement des modules en mémoire. Parfois, les modules profondément nichés ne sont pas "déchargés" proprement.~~
~~**L'évolution :** Le tracker *Deep Reload* utilisant `max(mtime)` sur de l'arbre permet de savoir quand purger l'instance globale.~~

### 5. Une interface (Index) plus "App-like"
**Le problème :** L'index actuel est une simple liste HTML classique.
**L'évolution :** Puisque le backend est KISS, l'index lui-même pourrait être une petite app `htag` en soi !
*   *Avantage :* Démontre la puissance de Htag au cœur même du manager, avec une vraie interface utilisateur dynamique (barre de recherche, belle présentation en grille des apps avec des icônes déduites, etc.).

### 6. Isolation des instances Htag (Multijoueur Actif)
**Le problème :** Actuellement, tous les utilisateurs partage la même instance `WebApp(app_class)` si elle est stockée dans la cache globale du backend `pye`. Les états de l'application peuvent donc déborder d'un utilisateur sur un autre.
**L'évolution :** Fournir une structure via une option ou configuration pour définir si on `spawn` (isole) la classe par utilisateur/connexion, ou si on sert une unique interface partagée par tous au niveau du serveur.
