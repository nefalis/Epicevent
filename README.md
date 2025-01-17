# Epic Events

C'est un système CRM en CLI (interface de ligne de commande) de gestion d'événements. Il permet de créer, mettre à jour et supprimer des utilisateurs, des clients, des contrats et des événements.

Ce projet utilise les technologies suivantes :
- Python
- MySQL : Base de données
- SQLAlchemy : ORM (Object Relational Mapper) pour interagir avec la base de données
- JWT : Utilisé pour la gestion des tokens de session
- Rich : Utilisé pour une interface en ligne de commande
- Pytest, Flake8 et Sentry : Outils de test et de gestion de la qualité du code


## Prérequis
- Pour utiliser cette application, vous devez avoir un serveur MySQL. Vous devez disposer d'un compte ayant les droits nécessaire.
- Python 🐍 doit être installé sur votre machine. Vous pouvez le télécharger depuis le site officiel de [Python](https://www.python.org/)

## Mise en place du projet

Créez un nouveau dossier sur votre bureau avec le nom de votre choix.
- Télécharger le contenu du projet ou clonez le avec le lien suivant :
```
https://github.com/nefalis/Epicevent.git
```
- Créez un environnement virtuel :
```
python -m venv env
```
- Activez l'environnement virtuel sous Windows :
```
env\Scripts\activate
```
- Activez l'environnement virtuel sous Linux :
```
source env/bin/activate
```
- Installez les dépendances :
```
pip install -r requirements.txt
```

## Configuration de la base de données
Avant d'initialiser la base de données, vous devez configurer MySQL. Assurez-vous que MySQL est installé et en cours d'exécution sur votre machine.

## Configuration de l'environnement

- Vous devez créer un fichier `.env` à la racine du projet avec le contenu suivant (en remplaçant les valeurs par celles de votre environnement) :
```
DATABASE_URL=mysql+pymysql://root:password@localhost/epicevent

SECRET_KEY=<votre_clé_unique>

SECRET_KEY_TOKEN=<votre_clé_unique_pour_jwt>
```
Remplacez **root** et **password** par votre nom d'utilisateur et votre mot de passe MySQL.

- Pour générer une clé unique pour pouvez éxécuter la commande suivante dans le terminal :
```
import secrets
print(secrets.token_hex(32))
```


- Pour créer les tables dans votre base de données MySQL, exécutez la commande suivante :
```
python setup_db.py
```
Ce script va initialiser la base de données et créer toutes les tables nécessaires, ainsi qu'un utilisateur administrateur par défaut.

## Lancement du programme

Numéro d'employé
```
ma2212
```
Password
```
Ef45632147f
```

Il ne vous reste plus qu'à lancer le fichier `main.py` et à vous connecter avec l'identifiant utilisateur et le mot de passe pour avoir accès au menu :

```
python main.py
```
Vous êtes connecté en tant que manager, vous aurez donc accès à tout, mais vous ne serez pas visible en tant qu'utilisateur si vous souhaitez voir les utilisateurs.

## Auteur
Charron Emilie
