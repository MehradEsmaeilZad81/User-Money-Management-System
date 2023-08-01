from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import GeneralSource, Subscription, Transaction, MoneyAccount
from .serializers import GeneralSourceSerializer, SubscriptionRequestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
# Create your views here.


class GeneralSourceView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    
    def get(self, request):
        generalsources = GeneralSource.objects.all()
        serializer = GeneralSourceSerializer(generalsources, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubscriptionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        general_source_name = serializer.validated_data['general_source_name']
        amount = serializer.validated_data['proposed_amount']
        general_source = GeneralSource.objects.filter(name=general_source_name).first()
        money_account = MoneyAccount.objects.filter(user=request.user).first()

        general_source.add_amount(amount)
        general_source.save()

        money_account.add_expense(amount)
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
