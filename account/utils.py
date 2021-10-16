from datetime import datetime

from django.utils.crypto import get_random_string


def genKey(phone):
    return str(phone) + str(datetime.date(datetime.now())) + "deepsense"
def genOtp():
    return get_random_string(6,allowed_chars="0123456789")




# def GenOtp():

