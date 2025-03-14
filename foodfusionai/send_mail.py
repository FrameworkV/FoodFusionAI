import smtplib
from email.message import EmailMessage
from pydantic import EmailStr
from foodfusionai.utils import project_config
from foodfusionai.CONFIG import get_config
config = get_config()

smtp_email = config.email
smtp_password = config.email_password

def registration_confirmation(username: str) -> str:
    email_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>Registrierung erfolgreich</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f6f6f6;
                display: flex;
                justify-content: flex-start;
                align-items: center;
                flex-direction: column;
                height: 100vh;
                padding-top: 50px;
            }}

            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}

            .email-header {{
                background-color: #85C1E9;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
                color: white;
            }}

            .email-header h1 {{
                margin: 0;
                font-size: 24px;
            }}

            .email-body {{
                padding: 20px;
                font-size: 16px;
                color: #333333;
            }}

            .email-body p {{
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>Registrierung erfolgreich!</h1>
            </div>
            <div class="email-body">
                <p>Hallo {username},</p>
                <p>Deine Registrierung bei FoodFusionAI war erfolgreich!</p>
                <p>Du kannst dich jetzt in dein Konto einloggen.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return email_content


def _html_code_verification_mail(username: str, token: str) -> str:
    if project_config['app']['status'] == "dev":
        confirmation_link = f"http://localhost:{project_config['api']['local']['port']}/users/verify/{token}"
    else:
        confirmation_link = f"{project_config['api']['hosted']['url']}/users/verify/{token}"

    email_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>Kontobestätigung</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f6f6f6;
            }}

            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}

            .email-header {{
                background-color: #007BFF;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
                color: white;
            }}

            .email-header h1 {{
                margin: 0;
                font-size: 24px;
            }}

            .email-body {{
                padding: 20px;
                font-size: 16px;
                color: #333333;
            }}

            .email-body p {{
                margin-bottom: 20px;
            }}

            .email-button {{
                display: block;
                width: 200px;
                margin: 20px auto;
                padding: 15px;
                text-align: center;
                background-color: #007BFF;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-size: 16px;
            }}

            .email-button:hover {{
                background-color: #3498DB;
            }}

            .email-footer {{
                text-align: center;
                font-size: 12px;
                color: #777777;
                padding: 20px;
                border-top: 1px solid #dddddd;
                margin-top: 20px;
            }}

            .email-footer a {{
                color: #5DADE2;
                text-decoration: none;
            }}

            .email-footer a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>Willkommen bei FoodFusionAI</h1>
            </div>
            <div class="email-body">
                <p>Hallo {username},</p>
                <p>Vielen Dank, dass du dich bei FoodFusionAI angemeldet hast. Bitte bestätige deine E-Mail-Adresse,
                    um dein Konto zu aktivieren und alle Funktionen nutzen zu können.</p>
                <p>Klicke einfach auf den Button unten, um dein Konto zu bestätigen:</p>
                <a href="{confirmation_link}" class="email-button">Konto bestätigen</a>
                <p>Falls du den Button nicht anklicken kannst, kopiere den folgenden Link in deinen Browser:</p>
                <p><a href="{confirmation_link}">Bestätigungslink</a></p>
                <p>Vielen Dank.</p>
            </div>
            <div class="email-footer">
                <p>Du hast diese E-Mail erhalten, weil du ein Konto bei FoodFusionAI erstellt hast. Falls du das nicht warst, ignoriere diese Mail bitte.</p>
                <p><a href="mailto:foodfusionai@gmail.com">Kontakt</a> | <a href="https://github.com/FrameworkV">GitHub</a> | <a href="[Coming soon]">Website</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return email_content

def send_verification_mail(to: EmailStr, username: str, token: str) -> None:
    msg = EmailMessage()
    msg.add_alternative(    
        _html_code_verification_mail(username, token),
        subtype="html"
    )

    msg["Subject"] = "Bestätigung deiner Registrierung bei FoodFusionAI"
    msg["From"] = smtp_email
    msg["To"] = to

    # send the message via our own SMTP server
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(smtp_email, smtp_password)
    server.send_message(msg)
    server.quit()


def _html_code_password_reset_mail(reset_code: int) -> str:
    email_content = f"""
            <!DOCTYPE html>
            <html lang="de">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="X-UA-Compatible" content="ie=edge">
                <title>Passwort zurücksetzen</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f6f6f6;
                    }}

                    .email-container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                    }}

                    .email-header {{
                        background-color: #007BFF;
                        padding: 20px;
                        text-align: center;
                        border-radius: 8px 8px 0 0;
                        color: white;
                    }}

                    .email-header h1 {{
                        margin: 0;
                        font-size: 24px;
                    }}

                    .email-body {{
                        padding: 20px;
                        font-size: 16px;
                        color: #333333;
                    }}

                    .email-body p {{
                        margin-bottom: 20px;
                    }}

                    .pin-code {{
                        display: block;
                        width: fit-content;
                        margin: 20px auto;
                        padding: 15px;
                        text-align: center;
                        border: 2px solid #007BFF;
                        color: #007BFF;
                        font-size: 20px;
                        letter-spacing: 2px;
                        border-radius: 5px;
                        font-weight: bold;
                        background-color: #ffffff; /* Make sure background stays white */
                    }}

                    .email-footer {{
                        text-align: center;
                        font-size: 12px;
                        color: #777777;
                        padding: 20px;
                        border-top: 1px solid #dddddd;
                        margin-top: 20px;
                    }}

                    .email-footer a {{
                        color: #5DADE2;
                        text-decoration: none;
                    }}

                    .email-footer a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-header">
                        <h1>Passwort zurücksetzen</h1>
                    </div>
                    <div class="email-body">
                        <p>Verwende den folgenden 6-stelligen PIN, um dein Passwort zurückzusetzen:</p>
                        <div class="pin-code">{reset_code}</div>
                    </div>
                    <div class="email-footer">
                        <p>Du hast diese E-Mail erhalten, weil du eine Anfrage zum Zurücksetzen deines Passworts bei FoodFusionAI gestellt hast. Falls du das nicht warst, kontaktiere uns bitte.</p>
                        <p><a href="mailto:foodfusionai@gmail.com">Kontakt</a> | <a href="https://github.com/FrameworkV">GitHub</a> | <a href="[Coming soon]">Website</a></p>
                    </div>
                </div>
            </body>
            </html>
            """

    return email_content

def send_password_reset_mail(to: EmailStr, reset_code: int) -> None:
    msg = EmailMessage()
    msg.add_alternative(
        _html_code_password_reset_mail(reset_code),
        subtype="html"
    )

    msg["Subject"] = "Zurücksetzen deines Passworts bei FoodFusionAI"
    msg["From"] = smtp_email
    msg["To"] = to

    # send the message via our own SMTP server
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(smtp_email, smtp_password)
    server.send_message(msg)
    server.quit()