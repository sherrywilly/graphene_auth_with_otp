import graphene
from graphene_django.filter import DjangoFilterConnectionField

from account.graphql.Type import UserType


class Query(graphene.ObjectType):
    all_users = DjangoFilterConnectionField(UserType)