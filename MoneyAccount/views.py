from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import GeneralSource, Subscription, Transaction, MoneyAccount
from .serializers import GeneralSourceSerializer, SubscriptionRequestSerializer, SubscriptionSerializer, SubscriptionMoneyRequestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
import jwt
from Authentication.models import User
from rest_framework.exceptions import AuthenticationFailed

# Create your views here.

def IsAuthenticated(request):
    token = request.COOKIES.get('jwt')

    if not token:
        raise AuthenticationFailed('Unauthenticated!, Please login to continue')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!, Please login to continue')

    user = User.objects.filter(id=payload['id']).first()
    return user


class GeneralSourceDetailView(APIView):
    def get(self, request, pk):
        user = IsAuthenticated(request)
        try:
            general_source = GeneralSource.objects.get(pk=pk)
        except GeneralSource.DoesNotExist:
            return Response({"detail": "GeneralSource not found."}, status=404)

        money_account = MoneyAccount.objects.filter(user=user).first()
        subscription = Subscription.objects.filter(general_source=general_source, money_account=money_account).first()
        if not subscription:
            return Response({"detail": "Subscription not found."}, status=404)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
    
    def post(self, request, pk):
        user = IsAuthenticated(request)
        money_account = MoneyAccount.objects.filter(user=user).first()
        general_source = GeneralSource.objects.filter(pk=pk).first()
        subscription = Subscription.objects.filter(general_source=general_source, money_account=money_account).first()
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

        Transaction.objects.create(
            money_account=money_account,
            general_source=general_source,
            amount=amount,
            transaction_type='W'
        )
        

class MySubscriptionView(APIView):
    def get(self, request):
        user = IsAuthenticated(request)
        money_account = MoneyAccount.objects.filter(user=user).first()
        subscriptions = Subscription.objects.filter(money_account=money_account)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

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
        general_source = GeneralSource.objects.filter(name=general_source_name).first()
        money_account = MoneyAccount.objects.filter(user=user).first()

        if Subscription.objects.filter(general_source=general_source, money_account=money_account).exists():
            return Response({
                'message': 'Subscription already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

        general_source.add_amount(amount)
        general_source.save()

        money_account.add_expense(amount)
        money_account.save()
        # Create the subscription for the logged-in user
        Subscription.objects.create(
            money_account=money_account,
            general_source=general_source,
            amount=amount,
        )

        Transaction.objects.create(
            money_account=money_account,
            general_source=general_source,
            amount=amount,
            transaction_type='D'
        )

        return Response({
            'message': 'Subscription created successfully. Waiting for approval.'
        }, status=status.HTTP_201_CREATED)
