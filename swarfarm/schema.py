import graphene

import bestiary.schema


class Query(
    bestiary.schema.Query,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query)
