from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .models import *
import re


def validate_account_duplication(email):
    account = Account.objects.filter(email=email).first()
    if account:
        raise ValidationError({"status": "failed", "parameter": "email", "message": "Account already exists"})


def validate_account_id(account_id):
    if not bool(re.match("^[A-Za-z0-9_.]*$", account_id)):
        raise ValidationError({"status": "failed", "parameter": "account_id", "message": "The account ID is invalid"})


def validate_password(password):
    if password.find(" ") != -1:
        raise ValidationError(
            {"status": "failed", "parameter": "password", "message": "The password cannot contain spaces"}
        )
    elif len(password) < 8:
        raise ValidationError(
            {"status": "failed", "parameter": "password", "message": "The password must be at least 8 characters"}
        )
