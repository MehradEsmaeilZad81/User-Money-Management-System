from rest_framework import serializers
from .models import GeneralSource

class GeneralSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSource
        fields = ('name', 'inventory', 'coefficient', 'deposit_interval', 'deposit_amount')

    
class SubscriptionRequestSerializer(serializers.Serializer):
    general_source_name = serializers.CharField(max_length=100)
    proposed_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        general_source_name = data.get('general_source_name')
        proposed_amount = data.get('proposed_amount')
        general_source = GeneralSource.objects.filter(name=general_source_name).first()
        if not general_source:
            raise serializers.ValidationError(
                'GeneralSource with name {} does not exist'.format(general_source_name))
        if not general_source.inventory > proposed_amount:
            raise serializers.ValidationError(
                'GeneralSource with name {} does not have sufficient inventory'.format(general_source_name))
        return data


# {
#     "general_source_name": "Number 1",
#     "proposed_amount": 1000.00
# }