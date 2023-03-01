from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
import mimetypes


def static(request):
    path = request.get_full_path()[1:]
    if path.find('?') != -1:
        path = path[:path.find('?')]
    if path[-1] == '/':
        path += 'index.html'

    for static_dir in settings.STATICFILES_DIRS:
        path = path.replace(settings.STATIC_URL.replace('/', ''), static_dir.split('/')[-1])
        try:
            file = open(path, 'rb')
            break
        except FileNotFoundError:
            file = None

    if file is not None:
        response = HttpResponse(content=file)
        response['Content-Type'] = mimetypes.guess_type(path)[0]
        return response
    else:
        return HttpResponseNotFound()
