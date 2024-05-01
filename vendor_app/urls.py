from django.urls import path, include
from .views import vendorViewset, purchaseOrderViewset, performanceViewset
from rest_framework import routers


# Create a DefaultRouter instance
router = routers.DefaultRouter()

# Register the 'vendorViewset' under the endpoint 'vendors'
router.register(r'vendors', vendorViewset)

# Register the 'purchaseOrderViewset' under the endpoint 'purchaseOrders'
router.register(r'purchaseOrders', purchaseOrderViewset)

# Register the 'performanceViewset' under the endpoint 'performances'
router.register(r'performances', performanceViewset)

# Define the URL patterns for the application
urlpatterns = [
    path('', include(router.urls)),
]
