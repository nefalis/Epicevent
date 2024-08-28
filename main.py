from config import engine, Base
from model.client_model import Client
from model.contract_model import Contract
from model.event_model import Event
from model.user_model import User


Base.metadata.create_all(bind=engine)
