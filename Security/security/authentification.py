import time
from Security.security.user_data_manager import get_user, update_user
from Security.security.password import verify_password
from Security.security.notifications import send_warning_email
from Security.security.configs import MAX_LOGIN_ATTEMPTS, DELAY_AFTER_3, DELAY_AFTER_4, DELAY_AFTER_5, TEMP_PASSWORD_VALIDITY


def verify_user_credentials(username: str, password: str):
    user = get_user(username)
    if not user:
        raise ValueError("Invalid username or password.")

    now = int(time.time())

    # Gestion du mot de passe temporaire
    if user.get("must_change_password", False):
        created_at = user.get("temp_password_created_at", 0)
        if now - created_at > TEMP_PASSWORD_VALIDITY:
            raise ValueError("Temporary password expired. Please request a new password reset.")

        # Vérifie si le mot de passe saisi correspond
        if verify_password(password, user["password_hash"].encode()):
            # Mot de passe temporaire OK : on exige de changer immédiatement le mot de passe
            return {"status": "must_change_password", "user": user}
        else:
            raise ValueError("Invalid temporary password.")

    # Authentification classique (mot de passe permanent)
    if not verify_password(password, user["password_hash"].encode()):
        # Ici ta logique de gestion des tentatives, blocages, etc.
        raise ValueError("Invalid username or password.")

    # Connexion OK, reset des flags éventuels
    if user.get("must_change_password"):
        update_user(username, "must_change_password", False)
        update_user(username, "temp_password_created_at", None)

    return {"status": "success", "user": user}