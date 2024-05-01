from django.shortcuts import render, redirect
from .models import *
from rest_framework import viewsets, status
from .serializers import vendorSerializer, purchaseOrderSerializer, PerformanceSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from rest_framework.exceptions import ValidationError


# Define a ViewSet for the 'vendor' model
class vendorViewset(viewsets.ModelViewSet):

    queryset = vendor.objects.all()
    serializer_class = vendorSerializer

    @action(detail=True, methods=["get"])
    def purchaseOrders(self, request, pk=None):
        vendorObj = self.get_object()
        purchaseOrders = purchaseOrder.objects.filter(vendor=vendorObj)
        serializer = purchaseOrderSerializer(
            purchaseOrders, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def performance(self, request, pk=None):
        vendor_obj = self.get_object()

        try:
            historical_performances = Performance.objects.filter(
                vendor=vendor_obj)
            serializer = PerformanceSerializer(
                historical_performances, many=True, context={"request": request}
            )
            return Response(serializer.data)

        except Performance.DoesNotExist:
            return Response(
                {"error": "No historical performance data exists for this vendor."}
            )


# Define a ViewSet for the 'purchaseOrder' model
class purchaseOrderViewset(viewsets.ModelViewSet):
    queryset = purchaseOrder.objects.all()
    serializer_class = purchaseOrderSerializer

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):

        purchase_order = self.get_object()

        if purchase_order.acknowledgementDate is None:
            purchase_order.acknowledgementDate = datetime.now()
            purchase_order.save()

            update_average_response_time(purchase_order)

            return Response(
                {"detail": "Acknowledgment successful."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Purchase order already acknowledged."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Define a ViewSet for the 'Performance' model
class performanceViewset(viewsets.ModelViewSet):

    queryset = Performance.objects.all()

    serializer_class = PerformanceSerializer

    def perform_create(self, serializer):
        vendor_id = self.request.data.get('vendor_id')

        if not vendor_id:
            raise ValidationError(
                "Vendor ID must be specified for Performance entry")

        try:
            vendor_instance = vendor.objects.get(pk=vendor_id)
        except vendor.DoesNotExist:
            raise ValidationError(
                "Vendor with the provided ID does not exist.")

        serializer.save(vendor=vendor_instance)
