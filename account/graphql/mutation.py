import base64
import datetime

import graphene
from django.contrib.auth import get_user_model
import pyotp as pyotp
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import F,Q
from graphql import GraphQLError
from graphql_jwt.refresh_token.shortcuts import create_refresh_token
from graphql_jwt.shortcuts import get_token
from django.utils import timezone
from account.models import UserOtp
from account.utils import genKey
from account.graphql.Type import UserType
import re
from django.contrib.auth.password_validation import validate_password
from django_graphene_permissions import permissions_checker
from django_graphene_permissions.permissions import IsAuthenticated

User = get_user_model()
EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
ONLY_NUM_REGEX = r"^[0-9]*$"

class CreateUserMutation(graphene.Mutation):
    class Arguments:
        phone = graphene.String()
        email = graphene.String()
        password = graphene.String()

    status = graphene.String()
    message = graphene.String()


    @classmethod
    def mutate(cls,root,info,phone,email,password):
        if x := cache.get(phone):
            print(f"=========={x}============")
            if x and x >= 5:
                m, s = divmod(cache.ttl(phone), 60)
                raise GraphQLError(f"please try again after {m} minutes  {s} seconds ")
            else:
                cache.set(phone, x + 1)
        if len(phone) !=10 and re.match(ONLY_NUM_REGEX,phone):
            raise GraphQLError("Mobile no should be 10 numbers") 
        elif email and not re.match(EMAIL_REGEX,email):
            raise GraphQLError("please provide a valid email")
        validate_password(password=password)
        if User.objects.filter(Q(mobile_number = phone)|Q(email=email)).exists():
            raise GraphQLError("User already exists")

        try:
            user = User.objects.create_user(mobile_number=phone,email= email,password= password)
            key = base64.b32encode(genKey(user.mobile_number).encode())
            otp = pyotp.TOTP(key, interval=300)
            userotp, _ = UserOtp.objects.get_or_create(user=user)
            userotp.otp = str(otp.now())
            userotp.save()
            cache.set(user.mobile_number,1,timeout=300)
            return CreateUserMutation(status="ok",
                                        message="you are successfully registered with our system")
        except Exception as e:
            raise GraphQLError(e)


class LoginMutation(graphene.Mutation):
    class Arguments:
        email_or_phone=graphene.String(required=True)
        password= graphene.String(required=True)
    status = graphene.String()
    message = graphene.String()
    token = graphene.String()
    refresh_token = graphene.String()
    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls,root,info,email_or_phone,password):
        try:
            __user = User.objects.get(Q(mobile_number=email_or_phone)|Q(email=email_or_phone))
        except User.DoesNotExist:
            raise GraphQLError("Invalid request with unregistered phone number")
        if  valid:=__user.check_password(password):
            if not __user.is_active:
                if x := cache.get(email_or_phone):
                    print(f"=========={x}============")
                    if x and x >= 5:
                        m, s = divmod(cache.ttl(email_or_phone), 60)
                        raise GraphQLError(f"please try again after {m} minutes  {s} seconds ")
                    else:
                        cache.set(email_or_phone, x + 1)
                else:
                    cache.set(email_or_phone, 1,timeout=300)
                key = base64.b32encode(genKey(__user.mobile_number).encode())
                otp = pyotp.TOTP(key, interval=300)
                print(otp.now())
                userotp ,_ = UserOtp.objects.get_or_create(user=__user)
                userotp.otp = str(otp.now())
                userotp.save()
                return LoginMutation(status="Fail",message="please verify your account to continue")

            else:
                __user.last_login = timezone.now()
                __user.save()
                return LoginMutation(status="ok",token=get_token(__user), refresh_token=str(create_refresh_token(__user)),
                                     user=__user,message ="successfully logged in")
        else:
            raise GraphQLError("please Try with valid credentials")





class VerifyOtpMutation(graphene.Mutation):
    class Arguments:
        phone_or_email = graphene.String(required=True)
        otp = graphene.String(required=True)

    token = graphene.String()
    refresh_token = graphene.String()
    user = graphene.Field(UserType)

    # user = graphene.
    @classmethod
    def mutate(cls, self, info, phone_or_email, otp):
        try:
            __user = User.objects.get(Q(mobile_number=phone_or_email)|Q(email=phone_or_email))
        except User.DoesNotExist:
            raise GraphQLError("Invalid request with unregistered phone number")
        if not __user.userotp.otp == otp:
            raise GraphQLError("invalid otp")

        __user.is_active= True
        __user.last_login = timezone.now()
        __user.save(force_update=True)
        cache.delete(phone_or_email)
        print("otp verification is successfully")

        return VerifyOtpMutation(token=get_token(__user), refresh_token=str(create_refresh_token(__user)),
                                     user=__user)




class ResendOTP(graphene.Mutation):
    status= graphene.String()
    message = graphene.String()
    class Arguments:
        phone_or_email = graphene.String(required=True)

    def mutate(self, info, phone_or_email):
        try:
            __user = User.objects.get(Q(mobile_number=phone_or_email) | Q(email=phone_or_email))
        except User.DoesNotExist:
            raise GraphQLError("Invalid request with unregistered phone number")
        if __user.is_active:
            raise GraphQLError("Invalid request")
        if x := cache.get(phone_or_email):
            print(f"=========={x}============")
            if x and x >= 5:
                m, s = divmod(cache.ttl(phone_or_email), 60)
                raise GraphQLError(f"please try again after {m} minutes  {s} seconds ")
            else:
                cache.set(phone_or_email, x + 1)
        else:
            cache.set(phone_or_email, 1, timeout=300)
        key = base64.b32encode(genKey(__user.mobile_number).encode())
        otp = pyotp.TOTP(key, interval=300)
        userotp, _ = UserOtp.objects.get_or_create(user=__user)
        userotp.otp = str(otp.now())
        userotp.save()
        return ResendOTP(status="ok",message="OTP sent to your mobile")

class ChangePassword(graphene.Mutation):
    mobile_number = graphene.String()
    message = graphene.String()

    class Arguments:
        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)
        new_password1 = graphene.String(required=True)

    @permissions_checker([IsAuthenticated])
    def mutate(self, info, old_password: str, new_password: str, new_password1: str):
        user = info.context.user
        if user.is_authenticated:

            if info.context.user.check_password(old_password):
                if str(new_password) == str(new_password1):
                    user_obj = User.objects.get(mobile_number=info.context.user.mobile_number)
                    user_obj.set_password(new_password)
                    user_obj.save(force_update=True)
                    return ChangePassword(mobile_number=info.context.user.mobile_number,
                                          message="Password Changed Successfully")
                else:
                    return ChangePassword(mobile_number=info.context.user.mobile_number,
                                          message='New password and confirm password not matching')
            else:
                return ChangePassword(mobile_number=info.context.user.mobile_number, message='Incorrect old password')
        else:
            return ChangePassword(mobile_number=None, message='No User Found')



class ForgotPassword(graphene.Mutation):
    class Arguments:
        mobile = graphene.String(required=True)

    status = graphene.String()
    message = graphene.String()

    def mutate(self,info,mobile):
        try:
            __user = User.objects.get(Q(mobile_number=mobile) | Q(email=mobile))
        except User.DoesNotExist:
            raise GraphQLError("Invalid request with unregistered phone number")
        key = base64.b32encode(genKey(__user.mobile_number).encode())
        otp = pyotp.TOTP(key, interval=300)
        print(otp.now())
        userotp, _ = UserOtp.objects.get_or_create(user=__user)
        userotp.otp = str(otp.now())
        userotp.save()

        return ResendOTP(status="ok",message="OTP sent to your mobile")


