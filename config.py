from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Configuration de la base de données
DATABASE_URL = "mysql+pymysql://root:Dpm6+Sq52814@localhost/epicevent"

# Créer l'instance
engine = create_engine(DATABASE_URL)

# Créer une classe de base pour les modèles
Base = declarative_base()

# Créer une session pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Configuration pour JWT
SECRET_KEY_TOKEN = os.getenv("SECRET_KEY_TOKEN")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
TOKEN_FILE = "authentication/token.txt"
