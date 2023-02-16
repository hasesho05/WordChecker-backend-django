from django.http.multipartparser import MultiPartParser
from app.models import *
from app.jwt_token import *


def permitGetToken(request):
    token = request.GET.get('token')
    if request.method != 'GET':
        queryDict, multiValueDict = MultiPartParser(request.META, request, request.upload_handlers).parse()
        token = queryDict.get('token')

    return token


def getUserInfo(request):
    token = permitGetToken(request)
    decoded_token = jwt_decode(token)

    if decoded_token['status'] == 'success':
        user = UserInfo.objects.get(id=decoded_token['data']['id'])
        request.user_info = user
        request.is_authenticated = True
    else:
        request.user_info = None
        request.is_authenticated = False


class GetUserInfoMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        getUserInfo(request)
