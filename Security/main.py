# ici un test globale du code
import time
from Security.security.user_data_manager import add_user, get_user, update_user, set_temporary_password
from Security.security.authentification import verify_user_credentials
from Security.security.access_control import has_permission
from Security.security.logs import log_action
from Security.security.otp import generate_otp_secret, verify_otp
from Security.security.password import hash_password
username = "testuser"
password = "TestUser$123"

from Security.security.password import hash_password
from Security.security.user_data_manager import update_user

update_user(username, "password_hash", hash_password(password).decode())
print(f"Mot de passe pour {username} réinitialisé dans la base.")


update_user(username, "password_hash", hash_password(password).decode())
print(f"Mot de passe pour {username} réinitialisé dans la base.")

def test_global_workflow():
    print("=== TEST GLOBAL DE SECURITE ET UTILISATEUR ===")

    username = "testuser"
    password = "TestUser$123"
    email = "testuser@example.com"
    new_password = "NewPass$456"

    # 1. Création utilisateur (ignore si existe)
    try:
        add_user(username, password, email)
        print(f"Utilisateur '{username}' créé.")
    except Exception as e:
        print(f"Utilisateur '{username}' existe déjà ou erreur : {e}")

    user = get_user(username)
    print(f"Utilisateur récupéré : {user}")

    # 2. Connexion correcte
    try:
        result = verify_user_credentials(username, password)
        print(f"Connexion réussie : {result}")
        log_action(username, "login_success")
    except Exception as e:
        print(f"Erreur connexion correcte : {e}")

    # 3. Tentatives de connexion échouées pour déclencher blocage
    print("Test blocage après tentatives échouées :")
    for i in range(6):
        try:
            verify_user_credentials(username, "WrongPassword!")
        except Exception as e:
            print(f"Tentative {i+1} échouée : {e}")
            log_action(username, "login_failed", details=f"Attempt {i+1}")

    # 4. Attente du délai de blocage (par exemple DELAY_AFTER_3)
    print("Attente du délai de blocage (65s)...")
    time.sleep(65)

    # 5. Connexion après délai
    try:
        result = verify_user_credentials(username, password)
        print(f"Connexion après délai blocage : {result}")
        log_action(username, "login_success_after_lock")
    except Exception as e:
        print(f"Erreur connexion après blocage : {e}")

    # 6. Génération mot de passe temporaire et test connexion avec
    temp_password = set_temporary_password(username)
    print(f"Mot de passe temporaire généré : {temp_password}")

    try:
        result = verify_user_credentials(username, temp_password)
        print(f"Connexion avec mot de passe temporaire : {result}")
        if result.get("status") == "must_change_password":
            # Simule changement mot de passe
            update_user(username, "password_hash", hash_password(new_password).decode())
            update_user(username, "must_change_password", False)
            update_user(username, "temp_password_created_at", None)
            print(f"Mot de passe changé avec succès pour {username}")
            log_action(username, "password_changed_after_temp")
    except Exception as e:
        print(f"Erreur connexion avec mot de passe temporaire : {e}")

    # 7. Test contrôle d'accès
    user = get_user(username)
    print(f"Test accès rôle '{user['role']}'")
    actions = ["delete_user", "view_profile", "edit_settings"]
    for action in actions:
        has_perm = has_permission(user, action)
        print(f"Action '{action}': accès = {has_perm}")
        log_action(username, "access_check", details=f"Action {action} - Allowed: {has_perm}")

    # 8. Test OTP
    otp_secret = generate_otp_secret()
    update_user(username, "otp_secret", otp_secret)
    update_user(username, "require_2fa", True)
    print(f"OTP secret généré : {otp_secret}")
    totp_code = pyotp.TOTP(otp_secret).now()
    print(f"Code OTP actuel : {totp_code}")

    try:
        otp_valid = verify_otp(username, totp_code)
        print(f"Validation OTP : {otp_valid}")
        log_action(username, "otp_success")
    except Exception as e:
        print(f"Erreur validation OTP : {e}")

    # Test OTP erroné
    try:
        verify_otp(username, "000000")
    except Exception as e:
        print(f"Erreur OTP attendu (faux code) : {e}")
        log_action(username, "otp_failed")

    print("=== FIN TEST GLOBAL ===")

if __name__ == "__main__":
    import pyotp
    test_global_workflow()
