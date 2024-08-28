from datetime import datetime
from model.user_model import User

def create_user(employee_number, complete_name, email, password, role, department):
    user = User(
        employee_number=employee_number,
        complete_name=complete_name,
        email=email,
        role=role,
        department=department,
        creation_date=datetime.now()
        )
    user.set_password(password)
    return user
