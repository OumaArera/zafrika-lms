import secrets
import string
from datetime import datetime
from ..models import Student


PREFIX = "HYM"


def generate_admission_number():
    year = datetime.now().year

    while True:
        numbers = "".join(secrets.choice(string.digits) for _ in range(3))
        letter = secrets.choice(string.ascii_uppercase)

        admission_number = f"{PREFIX}-{numbers}{letter}-{year}"

        if not Student.objects.filter(admission_number=admission_number).exists():
            return admission_number