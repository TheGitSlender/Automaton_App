import json
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from Security.security.password import hash_password, generate_strong_password
from Security.security.configs import TEMP_PASSWORD_VALIDITY


USER_FILE = "Security/data/users.json"
DATA_DIR = os.path.dirname(USER_FILE)

def ensure_data_dir_exists() -> None:
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

def load_users() -> List[Dict[str, Any]]:
    ensure_data_dir_exists()
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            f.write("[]")
        return []
    with open(USER_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users: List[Dict[str, Any]]) -> bool:
    ensure_data_dir_exists()
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)
    return True

def get_user(username: str) -> Optional[Dict[str, Any]]:
    users = load_users()
    for user in users:
        if user["username"].lower() == username.lower():
            return user
    return None

def add_user(username: str, password: str, email: str, role="user", require_2fa=True) -> dict:
    users = load_users()

    if get_user(username):
        raise ValueError(f"L'utilisateur '{username}' existe déjà")

    password_hash = hash_password(password).decode()

    new_user = {
        "username": username,
        "password_hash": password_hash,
        "email": email,
        "role": role,
        "is_locked": False,
        "login_attempts": 0,
        "login_count": 0,
        "require_2fa": require_2fa,
        "otp_secret": None,
        "created_at": int(time.time()),
        "last_login": None,
        "lock_until": None,
        "last_warning_sent": 0,
        "must_reset_password": False
    }

    users.append(new_user)
    save_users(users)

    return new_user


def update_user(username: str, field: str, value: Any) -> bool:
    users = load_users()
    updated = False
    for user in users:
        if user["username"].lower() == username.lower():
            user[field] = value
            updated = True
            break
    if not updated:
        raise ValueError("Utilisateur non trouvé")
    save_users(users)
    return True

def reset_password(username: str, new_password: str) -> bool:
    users = load_users()
    user_found = False
    for user in users:
        if user["username"].lower() == username.lower():
            from Security.security.password import hash_password

            user["password_hash"] = hash_password(new_password).decode()
            user["login_attempts"] = 0
            user["is_locked"] = False
            user_found = True
            break
    if not user_found:
        raise ValueError("Utilisateur non trouvé")
    save_users(users)
    return True

def set_temporary_password(username):
    """
    Génère un mot de passe temporaire, l'assigne à l'utilisateur, stocke la date de génération,
    et active le flag must_change_password.
    Retourne le mot de passe temporaire en clair (à envoyer par email).
    """
    users = load_users()
    temp_password = generate_strong_password(12)
    temp_password_hash = hash_password(temp_password).decode()
    now = int(time.time())
    updated = False

    for user in users:
        if user['username'].lower() == username.lower():
            user['password_hash'] = temp_password_hash
            user['temp_password_created_at'] = now
            user['must_change_password'] = True
            updated = True
            break

    if not updated:
        raise ValueError("User not found")

    save_users(users)
    return temp_password 