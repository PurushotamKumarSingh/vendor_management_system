# Import necessary modules from Django REST Framework
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# Import models from the current application
from .models import *

# Define a serializer for the 'vendor' model


class vendorSerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.ReadOnlyField()

    class Meta:
        model = vendor
        fields = ('id', 'name', 'address', 'vendor_code', 'contact_details')


# Define a serializer for the 'purchaseOrder' model
class purchaseOrderSerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.ReadOnlyField()

    class Meta:
        model = purchaseOrder
        fields = ('id', 'poNumber', 'vendor', 'orderDate', 'issueDate',
                  'deliveryDate', 'items', 'quantity', 'status')


# Define a serializer for the 'Performance' model
class PerformanceSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    vendor_id = serializers.IntegerField()

    class Meta:
        model = Performance
        fields = "__all__"

    def validate_vendor_id(self, value):
        if value is None:
            raise ValidationError(
                "Vendor ID must be specified for Performance entry")
        return value
