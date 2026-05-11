from datetime import datetime

current_year = datetime.now().year

def otp_template(otp: str) -> str:
    return f"""
    <div style="
        font-family: Arial, sans-serif;
        max-width: 600px;
        margin: auto;
        padding: 20px;
        border: 1px solid #e5e5e5;
        border-radius: 10px;
    ">
        <h2 style="color: #333;">Email Verification</h2>
        <p style="font-size: 16px; color: #555;">Hello,</p>
        <p style="font-size: 16px; color: #555;">
            Thank you for registering with us.
            Please use the following OTP to verify your email address:
        </p>
        <div style="text-align: center; margin: 30px 0;">
            <span style="
                display: inline-block;
                padding: 15px 30px;
                font-size: 32px;
                letter-spacing: 8px;
                font-weight: bold;
                color: #ffffff;
                background-color: #2563eb;
                border-radius: 8px;
            ">
                {otp}
            </span>
        </div>
        <p style="font-size: 15px; color: #777;">This OTP is valid for 10 minutes.</p>
        <p style="font-size: 15px; color: #777;">
            If you did not request this verification, please ignore this email.
        </p>
        <hr style="margin: 30px 0;" />
        <p style="font-size: 14px; color: #999; text-align: center;">
            (c) {current_year} DeepThinkAI. All rights reserved.
        </p>
    </div>
    """