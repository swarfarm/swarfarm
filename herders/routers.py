from rest_framework.routers import Route
from rest_framework_nested.routers import NestedDefaultRouter


class NestedStorageRouter(NestedDefaultRouter):
    routes = [
        # Detail route without identifier. Viewset must override get_object to work correctly.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
    ]
