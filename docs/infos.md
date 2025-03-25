# Documentation du Projet

## Structure du Projet

L'application est organisée selon la structure suivante :

```
menja-clic/
├── sources/       # Code source principal
├── data/          # Ressources statiques
└── docs/          # Documentation
```

## Description des Composants Principaux

### Fichiers

- **main.py** : Point d'entrée de l'application (gère les requêtes HTTP)
- **db.py** : Intéraction avec la base de données
- **db.db** : Base de données

### Dossiers

- **templates/** : Pages HTML
  - **client/** : Pages HTML pour les clients
  - **dashboard/** : Pages HTML pour les restaurateurs
  - **utils/** : Composants HTML réutilisables

## Possibilités d'Amélioration

### Ajout de Nouvelles Fonctionnalités

1. Créer de nouelles pages HTML dans `templates/`
2. Ajouter les points d'API requis dans `main.py`
3. Mettre à jour les fonctions de la base de données dans `db.py`
