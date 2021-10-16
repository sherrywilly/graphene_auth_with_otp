from django.contrib.auth import get_user_model
from graphene import Node
from graphene_django import DjangoObjectType

User = get_user_model()

class UserType(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (Node,)
        fields = ('mobile_number','email','is_superuser','is_active','is_professor')
        filter_fields = ['is_active', ]

