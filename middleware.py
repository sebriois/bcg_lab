import traceback

from django.conf import settings
from django.views.generic.simple import direct_to_template

METHOD_KEY = 'method'

class HttpMethodsMiddleware(object):
    """ Come from http://www.djangosnippets.org/snippets/174/
    
    This middleware allows developers to "fake" browser support for HTTP
    methods. Even though most modern browsers only support GET and POST,
    the HTTP standard defines others. In the context of REST, PUT and DELETE
    are used for client interaction with the server.
    """
    
    def process_request(self, request):
        if request.POST and METHOD_KEY in request.POST:
            if request.POST[METHOD_KEY].upper() in ['PUT', 'DELETE']:
                try:
                    request.method = request.POST['verb'].upper()
                except:
                    request.META['REQUEST_METHOD'] = request.REQUEST[METHOD_KEY].upper()
                if request.method == 'PUT' or request.META['REQUEST_METHOD'] == 'PUT':
                    if request.POST:
                      request.PUT = request.POST
                    elif request.GET:
                      request.PUT = request.GET

class ExceptionMiddleware(object):
    """
    Handle all non-catched exceptions.
    Correspond generally to HTTP error 500.
    """
    def process_exception(self, request, exception):
      if request.user.is_authenticated():
        return direct_to_template(request, '500.html', {
            'traceback': traceback.format_exc()
        })
