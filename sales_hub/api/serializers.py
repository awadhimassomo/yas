from rest_framework import serializers
from ..models import Customer, Interaction, Lead, Product, Purchase, SupportRequest

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'email', 'created_at']
        read_only_fields = ['created_at']

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ['id', 'customer', 'action_type', 'details', 'timestamp', 'agent', 'notes', 'is_completed', 'created_at']
        read_only_fields = ['timestamp', 'created_at']

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'customer', 'status', 'lead_type', 'notes', 'expected_close_date', 'value', 'assigned_to', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['id', 'customer', 'product', 'quantity', 'unit_price', 'total_amount', 'purchase_date', 'agent', 'notes', 'created_at']
        read_only_fields = ['total_amount', 'created_at']

class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = ['id', 'customer', 'request_type', 'subject', 'description', 'status', 'priority', 'assigned_to', 'resolved_at', 'resolution_notes', 'created_at']
        read_only_fields = ['resolved_at', 'created_at']

# Quick Services specific serializers
class PUKRetrievalSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    id_number = serializers.CharField(max_length=20)
    notes = serializers.CharField(required=False, allow_blank=True)

class BundlePurchaseSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    bundle_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(category='data_bundle'))
    payment_method = serializers.ChoiceField(choices=[('mpesa', 'M-Pesa'), ('card', 'Credit Card'), ('cash', 'Cash')])
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['bundle_id'].category != 'data_bundle':
            raise serializers.ValidationError("Selected product is not a data bundle")
        if data['amount'] < data['bundle_id'].price:
            raise serializers.ValidationError("Insufficient payment amount")
        return data
