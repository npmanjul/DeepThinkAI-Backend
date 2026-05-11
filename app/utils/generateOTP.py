import random

def generate_six_digit_otp() -> str:
    otp = "".join(
        str(random.randint(0, 9))
        for _ in range(6)
    )
    return otp