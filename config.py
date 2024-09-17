from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données
DATABASE_URL = "mysql+pymysql://root:Dpm6+Sq52814@localhost/epicevent"

# Créer l'instance
engine = create_engine(DATABASE_URL)

# Créer une classe de base pour les modèles
Base = declarative_base()

# Créer une session pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
