from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import jwt

from Authentication.models import User
from .models import GeneralSource, Subscription, Transaction, MoneyAccount
from .serializers import (
    GeneralSourceSerializer,
    SubscriptionRequestSerializer,
    SubscriptionSerializer,
    SubscriptionMoneyRequestSerializer,
    MoneyAccountSerializer,
    MoneyAccountRequestSerializer,
)


def IsAuthenticated(request):
    token = request.COOKIES.get('jwt')

    if not token:
        raise AuthenticationFailed(
            'Unauthenticated!, Please login to continue')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed(
            'Unauthenticated!, Please login to continue')

    user = User.objects.filter(id=payload['id']).first()
    return user


# Create your views here.

class GeneralSourceView(APIView):
    def get(self, request):
        user = IsAuthenticated(request)
        generalsources = GeneralSource.objects.all()
        serializer = GeneralSourceSerializer(generalsources, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = IsAuthenticated(request)
        serializer = SubscriptionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        general_source_name = serializer.validated_data['general_source_name']
        amount = serializer.validated_data['proposed_amount']
        general_source = GeneralSource.objects.filter(
            name=general_source_name).first()
        money_account = MoneyAccount.objects.filter(user=user).first()

        if Subscription.objects.filter(general_source=general_source, money_account=money_account).exists():
            return Response({
                'message': 'Subscription already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

        money_account.add_expense(amount)
        general_source.add_amount(amount)
        money_account.create_subscription(general_source, amount)
        money_account.create_transaction(general_source, amount, 'D')

        return Response({
            'message': 'Subscription created successfully. Waiting for approval.'
        }, status=status.HTTP_201_CREATED)


class MySubscriptionView(APIView):
    def get(self, request):
        user = IsAuthenticated(request)
        money_account = MoneyAccount.objects.filter(user=user).first()
        subscriptions = Subscription.objects.filter(
            money_account=money_account)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class GeneralSourceDetailView(APIView):
    def get(self, request, pk):
        user = IsAuthenticated(request)
        try:
            general_source = GeneralSource.objects.get(pk=pk)
        except GeneralSource.DoesNotExist:
            return Response({"detail": "GeneralSource not found."}, status=404)

        money_account = MoneyAccount.objects.filter(user=user).first()
        subscription = Subscription.objects.filter(
            general_source=general_source, money_account=money_account).first()
        if not subscription:
            return Response({"detail": "Subscription not found."}, status=404)

        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

    def post(self, request, pk):
        user = IsAuthenticated(request)
        money_account = MoneyAccount.objects.filter(user=user).first()
        general_source = GeneralSource.objects.filter(pk=pk).first()
        subscription = Subscription.objects.filter(
            general_source=general_source, money_account=money_account).first()
        if not subscription:
            return Response({"detail": "Subscription not found."}, status=404)

        serializer = SubscriptionMoneyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        if amount > subscription.coefficient_amount:
            return Response({"detail": "Amount is less than coefficient_amount."}, status=400)

        subscription.withdraw(amount)
        general_source.withdraw_amount(amount)
        money_account.add_income(amount)
        money_account.create_transaction(general_source, amount, 'W')

        return Response({"detail": "Withdrawal successful."}, status=200)


class MySubscriptionView(APIView):
    def get(self, request):
        user = IsAuthenticated(request)
        money_account = MoneyAccount.objects.filter(user=user).first()
        subscriptions = Subscription.objects.filter(
            money_account=money_account)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class MoneyAccountView(APIView):
    def get(self, request):
        user = IsAuthenticated(request)
        moneyaccounts = MoneyAccount.objects.all()
        serializer = MoneyAccountSerializer(moneyaccounts, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = IsAuthenticated(request)
        serializer = MoneyAccountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_reciver = User.objects.filter(
            email=serializer.validated_data['email']).first()

        sender = MoneyAccount.objects.filter(user=user).first()
        reciver = MoneyAccount.objects.filter(user=user_reciver).first()
        amount = serializer.validated_data['amount']

        if not reciver:
            return Response({"detail": "Reciver not found."}, status=404)

        if sender == reciver:
            return Response({"detail": "You can't send money to yourself."}, status=400)

        sender.add_expense(amount)
        reciver.add_income(amount)
        sender.create_usertransaction(reciver, amount)

        return Response({"detail": "Transaction successful."}, status=200)
