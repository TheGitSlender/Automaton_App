from dotenv import load_dotenv
import os

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "belbaraka.adam@ensam-casa.ma")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
DELAY_AFTER_3 = int(os.getenv("DELAY_AFTER_3", "60"))
DELAY_AFTER_4 = int(os.getenv("DELAY_AFTER_4", "300"))
DELAY_AFTER_5 = int(os.getenv("DELAY_AFTER_5", "86400"))
TEMP_PASSWORD_VALIDITY = int(os.getenv("TEMP_PASSWORD_VALIDITY", "120"))

MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
DEFAULT_USER_ROLE = os.getenv("DEFAULT_USER_ROLE", "user")

DATA_FOLDER = os.getenv("DATA_FOLDER", "Security/data")
USERS_FILE = os.getenv("USERS_FILE", f"{DATA_FOLDER}/users.json")
LOG_FILE = os.getenv("LOG_FILE", "Security/user_management.log")
