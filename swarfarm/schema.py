import graphene
from graphene_django.debug import DjangoDebug

import bestiary.schema


class Query(
    bestiary.schema.Query,
    graphene.ObjectType
):
    debug = graphene.Field(DjangoDebug, name='__debug')


schema = graphene.Schema(query=Query)
