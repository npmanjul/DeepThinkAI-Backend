import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_NAME = os.getenv("SENDER_NAME")


configuration = sib_api_v3_sdk.Configuration()

configuration.api_key["api-key"] = BREVO_API_KEY


api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)


def send_email(
    to_email: str,
    subject: str,
    html_content: str
):
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[
            {
                "email": to_email
            }
        ],

        sender={
            "name": SENDER_NAME,
            "email": SENDER_EMAIL
        },

        subject=subject,
        html_content=html_content,
    )
    try:
        response = api_instance.send_transac_email(
            send_smtp_email
        )
        print(response)
        return True
    except ApiException as e:
        print("Brevo Error:", e)
        return False