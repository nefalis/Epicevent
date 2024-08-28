from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from config import Base


class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    commercial_contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    remaining_price = Column(Numeric(10, 2), nullable=False)
    creation_date = Column(DateTime, nullable=False)
    statut = Column(String(50), nullable=False)

    client = relationship("Client", back_populates="contracts")
    events = relationship("Event", back_populates="contract")
    commercial_contact = relationship("User", back_populates="contracts_as_commercial")
