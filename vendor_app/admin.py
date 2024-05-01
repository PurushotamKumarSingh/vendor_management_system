from django.contrib import admin
from .models import *


# Define the administration settings for the 'vendor' model
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'vendor_code']


# Define the administration settings for the 'purchaseOrder' model
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['poNumber', 'vendor', 'orderDate', 'issueDate']


admin.site.register(Performance)
admin.site.register(vendor, CompanyAdmin)
admin.site.register(purchaseOrder, PurchaseOrderAdmin)
