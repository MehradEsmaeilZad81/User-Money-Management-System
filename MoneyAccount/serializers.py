from rest_framework import serializers
from .models import GeneralSource, Subscription, MoneyAccount


class GeneralSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSource
        fields = ('name', 'inventory', 'coefficient',
                  'deposit_interval', 'deposit_amount')


class SubscriptionRequestSerializer(serializers.ModelSerializer):
    general_source_name = serializers.CharField(max_length=100)
    proposed_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        general_source_name = data.get('general_source_name')
        proposed_amount = data.get('proposed_amount')
        general_source = GeneralSource.objects.filter(
            name=general_source_name).first()
        if not general_source:
            raise serializers.ValidationError(
                'GeneralSource with name {} does not exist'.format(general_source_name))
        if not general_source.inventory > proposed_amount:
            raise serializers.ValidationError(
                'GeneralSource with name {} does not have sufficient inventory'.format(general_source_name))
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('money_account', 'general_source',
                  'amount', 'coefficient_amount')


class SubscriptionMoneyRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('amount',)

    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        amount = data.get('amount')
        if not amount > 0:
            raise serializers.ValidationError(
                'Amount must be greater than 0')
        return data


class MoneyAccountSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = MoneyAccount
        fields = ('user_email', 'balance', 'income', 'expense')

    def get_user_email(self, obj):
        return obj.user.email


class MoneyAccountRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyAccount
        fields = ('email', 'amount')

    email = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        amount = data.get('amount')
        if not amount > 0:
            raise serializers.ValidationError(
                'Amount must be greater than 0')
        return data
