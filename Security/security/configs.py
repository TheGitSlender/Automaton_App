# configs.py
SMTP_SERVER = "smtp.gmail.com"                      
SMTP_PORT = 587
SMTP_EMAIL = "belbaraka.adam@ensam-casa.ma"          
SMTP_PASSWORD = "fodq kood mztw kwuj"              

MAX_LOGIN_ATTEMPTS = 5
DELAY_AFTER_3 = 60
DELAY_AFTER_4 = 300
DELAY_AFTER_5 = 86400
TEMP_PASSWORD_VALIDITY = 120  

MIN_PASSWORD_LENGTH = 8          
DEFAULT_USER_ROLE = "user"         # Rôle attribué par défaut à un nouvel utilisateur

DATA_FOLDER = "Security/data"
USERS_FILE = f"{DATA_FOLDER}/users.json"
LOG_FILE = "Security/user_management.log"
