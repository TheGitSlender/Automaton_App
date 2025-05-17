# Génération et validation de codes OTP (2FA)
import pyotp
from Security.security.user_data_manager import get_user

def generate_otp_secret():
    return pyotp.random_base32()

def verify_otp(username: str, otp_code: str) -> bool:
    user = get_user(username)
    if not user or not user.get("require_2fa") or not user.get("otp_secret"):
        raise ValueError("2FA non activée ou utilisateur non trouvé")
    totp = pyotp.TOTP(user["otp_secret"])
    if not totp.verify(otp_code):
        raise ValueError("Code OTP invalide")
    return True
