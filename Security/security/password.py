# Hachage, vérification des mots de passe
import bcrypt 
import random
import string

# hasher le mot de passe, qui est stocke dans la variable password
def hash_password(password):
    # Pour des raison de calcule j ai pris la valeur de salt par defaut 12, plus le salt est grand, plus le hash est calculable dans une grande durée, donc ca resiste contre les attaques bruteforce 
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)) 


# Vérification d'un mot de passe
def verify_password(password, password_hashed):
    return bcrypt.checkpw(password.encode(), password_hashed)

# proposer un mot de passe fort 
def generate_strong_password(length=12):
    if length < 8:
        raise ValueError("La longueur du mot de passe doit être d'au moins 8 caractères.")

    # Garantir au moins une majuscule, une minuscule, un chiffre, et un caractère special
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*()-_=+[]}{;:,.<>?")
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.<>?"
    remaining = [random.choice(all_chars) for _ in range(length - 4)]
    password_list = list(upper + lower + digit + special + ''.join(remaining))
    random.shuffle(password_list)
    return ''.join(password_list)


