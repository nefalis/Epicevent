from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config import Base


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=True)
    creation_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)
    commercial_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    contracts = relationship("Contract", back_populates="client")
    events = relationship("Event", back_populates="client")
    commercial_contact = relationship("User", back_populates="clients")


from model.user_model import User
from model.contract_model import Contract
from model.event_model import Event