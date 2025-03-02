from django.db import models
import uuid

class ProcessingRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    webhook_url = models.URLField(blank=True, null=True)  # Optional webhook URL

class Image(models.Model):
    request = models.ForeignKey(ProcessingRequest, related_name='images', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    input_url = models.URLField()
    output_url = models.URLField(blank=True, null=True)  # Set after processing
    status = models.CharField(max_length=20, default="PENDING")  # PENDING, SUCCESS, FAILED

