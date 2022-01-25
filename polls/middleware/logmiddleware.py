import datetime

from django.core.handlers.wsgi import WSGIRequest as Request

from polls.models import GeneralLog


class LogMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request: Request, view_func, view_args, view_kwargs):
        request.META["HTTP_X_CSRFTOKEN"] = request.COOKIES.get("csrftoken")
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        user_agent = request.META.get('HTTP_USER_AGENT')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        GeneralLog(ip=ip, user_agent=user_agent, access_time=datetime.datetime.now()).save()
        return None
