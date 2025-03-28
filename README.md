# MENJA'CLICK

## Python

- Python 3.12.3

## Consignes d'installation

Suivre les étapes suivantes pour installer le projet localement :

1. Cloner le projet si vous avez git d'installé sinon télécharger le projet en zip :

```bash
git clone https://github.com/rixquli/menja-clic.git
```

2. Se rendre dans le dossier du projet :

```bash
cd menja-clic
```

3. Se rendre dans le dossier du projet :

```bash
cd sources
```

4. Installer les librairies :

```bash
pip install -r requirements.txt
```

5. Lancer le serveur :

```bash
python main.py
```

6. Accéder à l'interface en ouvrant un navigateur à l'adresse :

```bash
http://127.0.0.1:5000
```

#### Ou bien :

**Pour tout faire en une seule commande :**

```bash
git clone https://github.com/rixquli/menja-clic.git
cd menja-clic/sources
pip install -r requirements.txt
python main.py
```

Sinon, vous pouvez accéder à l'interface en ligne à l'adresse suivante : [MENJA'CLICK](https://menjaclic-9d4ff48bbfb7.herokuapp.com)

## Pour se connecter à l'interface administrateur

- Identifiant : `a`
- Mot de passe : `a`

## Pour se connecter à l'interface client

- Identifiant : `d`
- Mot de passe : `d`

## Liste des librairie

- blinker==1.9.0
- cachelib==0.13.0
- click==8.1.8
- colorama==0.4.6
- Flask==3.1.0
- Flask-Session==0.8.0
- itsdangerous==2.2.0
- Jinja2==3.1.6
- MarkupSafe==3.0.2
- msgspec==0.19.0
- Werkzeug==3.1.3
- gunicorn

## Description des pages

### Pages Cantinieres

- Stockage
- liste reservation

### Pages Client

- Liste des produits
- Panier
- Liste des commandes
