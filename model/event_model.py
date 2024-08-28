from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config import Base

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(255), nullable=False)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client_name = Column(String(255), nullable=False)
    client_contact = Column(String(400), nullable=False)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    support_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    location = Column(String(255), nullable=False)
    attendees = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    client = relationship("Client", back_populates="events")
    contract = relationship("Contract", back_populates="events")
    support_contact = relationship("User", back_populates="events_as_support")
