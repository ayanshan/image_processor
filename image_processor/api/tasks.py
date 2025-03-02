from celery import shared_task
from .models import ProcessingRequest, Image
from processing.image_utils import compress_image

@shared_task
def process_images_async(request_id):
    """Processes images asynchronously."""
    try:
        request_obj = ProcessingRequest.objects.get(id=request_id)
        request_obj.status = "PROCESSING"
        request_obj.save()

        for image_obj in request_obj.images.all():
            try:
                output_path = f'media/compressed_{image_obj.id}.jpg'
                compress_image(image_obj.input_url, output_path)

                image_obj.output_url = f'/media/compressed_{image_obj.id}.jpg'
                image_obj.status = "SUCCESS"
                image_obj.save()
            except Exception:
                image_obj.status = "FAILED"
                image_obj.save()

        request_obj.status = "COMPLETED"
        request_obj.save()
    except ProcessingRequest.DoesNotExist:
        return

