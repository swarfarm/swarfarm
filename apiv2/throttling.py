from rest_framework.throttling import ScopedRateThrottle


# Limit the number of POSTs to a certain scope, but use normal rates for other request methods.
class ScopedPostRequestThrottle(ScopedRateThrottle):
    scope_attr = 'throttle_scope'

    def get_cache_key(self, request, view):
        if request.method == 'POST':
            ident = self.get_ident(request)

            return self.cache_format % {
                'scope': self.scope,
                'ident': ident
            }

        return None
