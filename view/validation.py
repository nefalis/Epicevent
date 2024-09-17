import re

def validate_text(text: str) -> bool:
    """Vérifie que le texte contient uniquement des lettres, espaces et certains caractères spéciaux appropriés."""
    return bool(re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ '-]+$", text))

def validate_email(email: str) -> bool:
    """Valide que l'email est dans un format correct."""
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))

def validate_phone_number(phone: str) -> bool:
    """
    Valide que le numéro de téléphone contient uniquement des chiffres et respecte une longueur correcte.
    """
    return bool(re.match(r"^\d{10}$", phone))

def validate_digits(value: str) -> bool:
    """
    Vérifie que la saisie contient uniquement des chiffres.
    """
    return bool(re.match(r"^\d+$", value))

def validate_employee_number(employee_number: str) -> bool:
    """
    Valide que le numéro d'employé est composé de 2 lettres suivies de 4 chiffres.
    Ex : AB1234
    """
    return bool(re.match(r"^[A-Za-z]{2}\d{4}$", employee_number))

def validate_password(password: str) -> bool:
    """
    Valide que le mot de passe contient au moins 8 caractères, une majuscule, 
    une minuscule, et un chiffre.
    """
    return bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$", password))