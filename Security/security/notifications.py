import smtplib
from email.mime.text import MIMEText
from Security.security.configs import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD


def send_warning_email(user_email: str, username: str):
    subject = "Security Alert – Suspicious Login Attempt"
    body = f"""
Hello {username},

We detected a failed login attempt on your account.

If this wasn't you, please secure your account immediately by changing your password.

This is an automated message. Do not reply.

Best regards,
Security Team - CSCC-12
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = user_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, [user_email], msg.as_string())
        server.quit()
        print(f" Alert email sent to {user_email}")
    except Exception as e:
        print(f" Failed to send alert email: {e}")
def send_temporary_password_email(user_email: str, username: str, temp_password: str, validity_minutes: int = 10):
    subject = "Temporary Password for Your Account"
    body = f"""
Hello {username},

You requested a password reset. Here is your temporary password (valid for {validity_minutes} minutes):

    {temp_password}

Please use this password to log in. For security reasons, you will be required to set a new password immediately after logging in.

If you did not request this reset, please contact support or ignore this message.

Best regards,
Security Team - CSCC-12
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = user_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, [user_email], msg.as_string())
        server.quit()
        print(f"Temporary password email sent to {user_email}")
    except Exception as e:
        print(f"Failed to send temporary password email: {e}")