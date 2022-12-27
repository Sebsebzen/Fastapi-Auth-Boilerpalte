import os
import smtplib
from email.message import EmailMessage
from fastapi import requests
import logging
logging.getLogger('root')

EMAIL = os.getenv("MAILGUN_EMAIL")
PASSWORD = os.getenv("MAILGUN_PASSWORD")
API_KEY = os.getenv("MAILGUN_API_KEY")


def send_mail(to, token, username, pin, email=EMAIL, password=PASSWORD):
    msg = EmailMessage()
    msg.add_alternative(
        f"""\
<html>
  <head>

    <title>Document</title>
  </head>
  <body>
    <div id="box">
      <h2>Hallo {username},</h2> 
        <p>Please click
            <a href="http://localhost:8000/verify/{token}">
                here
            </a> to confirm your registration.
        </p>
        <p>Or use the following pin when logged in: <b>{pin}</b>
        </p>
      </form>
    </div>
  </body>
</html>

<style>
  #box {{
    margin: 0 auto;
    max-width: 500px;
    border: 1px solid black;
    height: 200px;
    text-align: center;
    background: lightgray;
  }}

  p {{
    padding: 10px 10px;
    font-size: 18px;
  }}

  .inline {{
    display: inline;
  }}

  .link-button {{
    background: none;
    border: none;
    color: blue;
    font-size: 22px;
    text-decoration: underline;
    cursor: pointer;
    font-family: serif;
  }}
  .link-button:focus {{
    outline: none;
  }}
  .link-button:active {{
    color: red;
  }}
</style>
    """,
        subtype="html",
    )

    msg["Subject"] = "Confirm your registration"
    msg["From"] = email
    msg["To"] = to

    try:
      logging.info("Sending email...")
      logging.info(f"To: {to}, PIN: {pin}")
      server = smtplib.SMTP_SSL("smtp.mailgun.org", 465)
      server.login(email, password)
      server.send_message(msg)
      server.quit()
      logging.info("Email sent")
    except Exception as e:
     logging.info(f"Error sending email: {e}")


# def send_mail(to, token, username, email=email, password=password):
# 	return requests.post(
# 		"https://api.mailgun.net/v3/sandboxf9238eb2a4d644789ba080fd0bcaa64e.mailgun.org",
# 		auth=("api", API_KEY),
# 		data={"from": "Excited User <mailgun@YOUR_DOMAIN_NAME>",
# 			"to": ["bar@example.com", "YOU@YOUR_DOMAIN_NAME"],
# 			"subject": "Hello",
# 			"text": "Testing some Mailgun awesomness!"})