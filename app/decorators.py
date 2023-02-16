from .models import *
from .jwt_token import *


def permitGetToken(request):
    token = request.GET.get('token')
    if request.method != 'GET':
        token = request.data.get('token')

    return token


def getAccount(request):
    token = permitGetToken(request)
    decoded_token = jwt_decode(token)
    request.account = None
    request.token = None
    request.is_authenticated = False

    if decoded_token['status'] == 'success':
        account = Account.objects.filter(id=decoded_token['data']['id']).first()

        if account:
            request.account = account
            request.token = token
            request.is_authenticated = True


def get_account(func):
    def wrapper(obj, request, *args, **kwargs):
        try:
            getAccount(request)
        except:
            pass
        return func(obj, request, *args, **kwargs)

    return wrapper
