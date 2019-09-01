from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse

from herders.models import Summoner


# Base view classes
class SummonerMixin:
    summoner = None

    def dispatch(self, request, *args, **kwargs):
        profile_name = kwargs.get('profile_name')

        if profile_name:
            try:
                self.summoner = Summoner.objects.select_related('user').get(
                    user__username__iexact=kwargs.get('profile_name'),
                )
                username = self.summoner.user.username

                if username != profile_name:
                    # Redirect to correct URL on an incorrect case mismatch
                    kwargs['profile_name'] = username
                    return HttpResponseRedirect(reverse(self.request.resolver_match.view_name, kwargs=kwargs))

                return super().dispatch(request, *args, **kwargs)
            except Summoner.DoesNotExist:
                return HttpResponseNotFound()

    def get_context_data(self, **kwargs):
        kwargs['profile_name'] = self.kwargs.get('profile_name')
        kwargs['summoner']: self.summoner
        return super().get_context_data(**kwargs)


class IsOwnerMixin:
    """
    Provides function/context if the user viewing the page is the owner of the account being requested
    """
    def is_owner(self):
        return self.request.user.username == self.kwargs.get('profile_name')

    def get_context_data(self, **kwargs):
        kwargs['is_owner'] = self.test_func()
        return super().get_context_data(**kwargs)


class OwnerRequiredMixin(IsOwnerMixin, UserPassesTestMixin):
    """
    Requires that the logged in user is the owner of the account being requested
    """
    raise_exception = True
    permission_denied_message = 'Must be acount owner to view this page'

    def test_func(self):
        return self.is_owner()
