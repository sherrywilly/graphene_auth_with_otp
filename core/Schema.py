import graphql_jwt
from graphene.types.schema import Schema
import graphene
from account.graphql.mutation import CreateUserMutation, VerifyOtpMutation, LoginMutation, ResendOTP, ChangePassword, \
    ForgotPassword
from account.graphql.query import  Query as AccountQuery
class Query(AccountQuery, graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    create_user = CreateUserMutation.Field()
    verify_otp = VerifyOtpMutation.Field()
    login_user = LoginMutation.Field()
    resend_otp = ResendOTP.Field()
    change_pass = ChangePassword.Field()
    forgot_pass = ForgotPassword.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
Schema = Schema(query=Query,mutation=Mutation)