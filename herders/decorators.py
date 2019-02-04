from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseNotFound, HttpResponseRedirect


def username_case_redirect(function):
    def wrap(request, *args, **kwargs):
        profile_name = kwargs.get('profile_name')
        if profile_name:
            try:
                username = User.objects.get(username__iexact=profile_name).username
                if username != profile_name:
                    kwargs['profile_name'] = username
                    return HttpResponseRedirect(reverse(request.resolver_match.view_name, kwargs=kwargs))
            except User.DoesNotExist:
                return HttpResponseNotFound()
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
