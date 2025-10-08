from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..models import Customer, Interaction, Lead, Product, Purchase, SupportRequest
from .serializers import (
    CustomerSerializer, InteractionSerializer, LeadSerializer,
    ProductSerializer, PurchaseSerializer, SupportRequestSerializer,
    PUKRetrievalSerializer, BundlePurchaseSerializer
)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'phone', 'email']
    filterset_fields = ['is_active']

class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['action_type', 'is_completed', 'agent']
    search_fields = ['customer__name', 'notes']

    def perform_create(self, serializer):
        serializer.save(agent=self.request.user.agent if hasattr(self.request.user, 'agent') else None)

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'lead_type', 'is_active', 'assigned_to']
    search_fields = ['customer__name', 'notes']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product__category', 'purchase_date']
    search_fields = ['customer__name', 'product__name']

    def perform_create(self, serializer):
        serializer.save(
            agent=self.request.user.agent if hasattr(self.request.user, 'agent') else None,
            total_amount=serializer.validated_data['quantity'] * serializer.validated_data['unit_price']
        )

class SupportRequestViewSet(viewsets.ModelViewSet):
    queryset = SupportRequest.objects.all()
    serializer_class = SupportRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'priority', 'request_type', 'assigned_to']
    search_fields = ['customer__name', 'subject', 'description']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        support_request = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        support_request.status = 'resolved'
        support_request.resolution_notes = resolution_notes
        support_request.resolved_at = timezone.now()
        support_request.save()
        
        return Response({'status': 'support request resolved'})

# Quick Services API Views
class PUKRetrievalView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = PUKRetrievalSerializer(data=request.data)
        if serializer.is_valid():
            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                phone=serializer.validated_data['phone_number'],
                defaults={'name': f"Customer {serializer.validated_data['phone_number']}"}
            )
            
            # Log the interaction
            interaction = Interaction.objects.create(
                customer=customer,
                action_type='support',
                notes=f"PUK retrieval requested. ID: {serializer.validated_data['id_number']}. {serializer.validated_data.get('notes', '')}",
                agent=request.user.agent if hasattr(request.user, 'agent') else None,
                details={
                    'service_type': 'puk_retrieval',
                    'id_number': serializer.validated_data['id_number'],
                    'status': 'completed'
                }
            )
            
            return Response({
                'status': 'success',
                'message': 'PUK retrieval request processed',
                'interaction_id': interaction.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BundlePurchaseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = BundlePurchaseSerializer(data=request.data)
        if serializer.is_valid():
            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                phone=serializer.validated_data['phone_number'],
                defaults={'name': f"Customer {serializer.validated_data['phone_number']}"}
            )
            
            bundle = serializer.validated_data['bundle_id']
            
            # Create purchase record
            purchase = Purchase.objects.create(
                customer=customer,
                product=bundle,
                quantity=1,
                unit_price=bundle.price,
                total_price=bundle.price,
                payment_method=serializer.validated_data['payment_method'],
                agent=request.user.agent if hasattr(request.user, 'agent') else None,
                notes=serializer.validated_data.get('notes', '')
            )
            
            # Log the interaction
            interaction = Interaction.objects.create(
                customer=customer,
                action_type='purchase',
                notes=f"Data bundle purchased: {bundle.name}",
                agent=request.user.agent if hasattr(request.user, 'agent') else None,
                details={
                    'service_type': 'bundle_purchase',
                    'bundle_id': bundle.id,
                    'bundle_name': bundle.name,
                    'amount': str(bundle.price),
                    'payment_method': serializer.validated_data['payment_method'],
                    'purchase_id': purchase.id,
                    'status': 'completed'
                }
            )
            
            return Response({
                'status': 'success',
                'message': f'Successfully purchased {bundle.name} bundle',
                'purchase_id': purchase.id,
                'interaction_id': interaction.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
