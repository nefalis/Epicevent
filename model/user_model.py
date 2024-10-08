import bcrypt
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    employee_number = Column(String(30), unique=True, nullable=False)
    complete_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    department_id = Column(
        Integer, ForeignKey('departments.id'), nullable=False
        )
    creation_date = Column(DateTime, nullable=False)

    department = relationship("Department", back_populates="users")
    clients = relationship("Client", back_populates="commercial_contact")
    contracts_as_commercial = relationship(
        "Contract", back_populates="commercial_contact"
        )
    events_as_support = relationship(
        "Event", back_populates="support_contact"
        )

    def set_password(self, raw_password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
        self.password = hashed.decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.checkpw(
            raw_password.encode('utf-8'), self.password.encode('utf-8')
            )


class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    users = relationship("User", back_populates="department")
