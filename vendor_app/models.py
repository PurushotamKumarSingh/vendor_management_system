# Import necessary modules from Django
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from django.utils import timezone


# Define the 'vendor' model
class vendor(models.Model):

    name = models.CharField(max_length=100)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=100)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def __str__(self):
        return self.name


# Define the 'purchaseOrder' model
class purchaseOrder(models.Model):

    vendor = models.ForeignKey(vendor, on_delete=models.CASCADE)
    poNumber = models.CharField(max_length=100)
    orderDate = models.DateTimeField()
    deliveryDate = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=100)
    issueDate = models.DateTimeField()
    acknowledgementDate = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.poNumber} {self.vendor.name}"


# Define the 'Performance' model
class Performance(models.Model):

    vendor = models.ForeignKey(vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    onTimeDeliveryRate = models.FloatField(blank=True, null=True)
    qualityRatingAvg = models.FloatField(blank=True, null=True)
    averageResponseTime = models.FloatField(blank=True, null=True)
    fulfillmentRate = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.vendor.name


# Define a signal to update vendor performance metrics when a purchase order is saved
@receiver(post_save, sender=purchaseOrder)
def on_purchase_order_save(sender, instance, **kwargs):
    update_on_time_delivery_rate(instance)
    update_quality_rating_avg(instance)
    update_fulfillment_rate(instance)
    create_historical_performance(instance)


def update_on_time_delivery_rate(po_instance):
    if po_instance.status == 'completed':
        completed_purchases = purchaseOrder.objects.filter(
            vendor=po_instance.vendor,
            status='completed',
            deliveryDate__lte=po_instance.deliveryDate
        ).count()

        total_completed_purchases = purchaseOrder.objects.filter(
            vendor=po_instance.vendor,
            status='completed'
        ).count()

        on_time_delivery_rate = completed_purchases / \
            total_completed_purchases if total_completed_purchases > 0 else 0

        po_instance.vendor.on_time_delivery_rate = on_time_delivery_rate
        po_instance.vendor.save()


def update_quality_rating_avg(po_instance):
    if po_instance.status == 'completed' and po_instance.quantityRating is not None:
        completed_purchases = purchaseOrder.objects.filter(
            vendor=po_instance.vendor,
            status='completed',
            quantityRating__isnull=False
        )

        total_ratings = sum(
            [purchase.quantityRating for purchase in completed_purchases])
        quality_rating_avg = total_ratings / \
            completed_purchases.count() if completed_purchases.count() > 0 else 0

        po_instance.vendor.quality_rating_avg = quality_rating_avg
        po_instance.vendor.save()


def update_average_response_time(po_instance):
    if po_instance.acknowledgementDate is not None:
        response_times = purchaseOrder.objects.filter(
            vendor=po_instance.vendor,
            acknowledgementDate__isnull=False
        ).exclude(issueDate__isnull=True)

        total_response_time_seconds = sum(
            [(purchase.issueDate-purchase.acknowledgementDate).total_seconds() for purchase in response_times])
        total_response_time_days = total_response_time_seconds / \
            (60 * 60 * 24)  # Convert seconds to days
        average_response_time_days = total_response_time_days / \
            response_times.count() if response_times.count() > 0 else 0

        po_instance.vendor.average_response_time = average_response_time_days
        po_instance.vendor.save()


def update_fulfillment_rate(po_instance):
    fulfilled_purchases = purchaseOrder.objects.filter(
        vendor=po_instance.vendor,
        status='completed',
        quantityRating__isnull=False
    )

    total_fulfilled_purchases = purchaseOrder.objects.filter(
        vendor=po_instance.vendor,
        status='completed'
    )

    fulfillment_rate = fulfilled_purchases.count(
    ) / total_fulfilled_purchases.count() if total_fulfilled_purchases.count() > 0 else 0

    po_instance.vendor.fulfillment_rate = fulfillment_rate
    po_instance.vendor.save()


def create_historical_performance(po_instance):
    if po_instance.status == 'completed':
        vendor = po_instance.vendor

        # Use delivery date of the purchase order for historical performance date
        historical_date = po_instance.deliveryDate

        # Check if a historical performance entry already exists for the vendor on the given date
        historical_performance, created = Performance.objects.get_or_create(
            vendor=vendor,
            date=historical_date,
            defaults={
                'onTimeDeliveryRate': vendor.on_time_delivery_rate,
                'qualityRatingAvg': vendor.quality_rating_avg,
                'averageResponseTime': vendor.average_response_time,
                'fulfillmentRate': vendor.fulfillment_rate,
            }
        )

        # If the historical performance entry already exists, update its fields
        if not created:
            historical_performance.onTimeDeliveryRate = vendor.on_time_delivery_rate
            historical_performance.qualityRatingAvg = vendor.quality_rating_avg
            historical_performance.averageResponseTime = vendor.average_response_time
            historical_performance.fulfillmentRate = vendor.fulfillment_rate

            # Save the changes
            historical_performance.save()
