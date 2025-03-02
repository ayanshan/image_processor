import csv
import re
from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import ProcessingRequest, Image
from processing.image_utils import compress_image
from .tasks import process_images_async

URL_PATTERN = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_csv(request):
    """Handles CSV upload, validates data, and triggers async processing."""
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file provided'}, status=400)

    request_obj = ProcessingRequest.objects.create()
    decoded_file = file.read().decode('utf-8').splitlines()
    reader = csv.reader(decoded_file)

    header = next(reader, None)
    if header != ["S. No.", "Product Name", "Input Image Urls"]:
        return Response({'error': 'Invalid CSV format'}, status=400)

    for row in reader:
        if len(row) != 3:
            return Response({'error': 'Invalid row format'}, status=400)

        serial_no, product_name, input_urls = row
        input_urls = input_urls.split(',')

        for url in input_urls:
            url = url.strip()
            if not re.match(URL_PATTERN, url):
                return Response({'error': f'Invalid URL: {url}'}, status=400)

            Image.objects.create(request=request_obj, product_name=product_name, input_url=url)

    process_images_async.delay(str(request_obj.id))  # ✅ Triggers async task
    return Response({'request_id': str(request_obj.id)})

@api_view(['GET'])
def check_status(request, request_id):
    """Returns processing status."""
    try:
        request_obj = ProcessingRequest.objects.get(id=request_id)
        images = request_obj.images.all()
        return Response({
            'request_id': request_id,
            'status': request_obj.status,
            'images': [{'input_url': img.input_url, 'output_url': img.output_url, 'status': img.status} for img in images]
        })
    except ProcessingRequest.DoesNotExist:
        return Response({'error': 'Request ID not found'}, status=404)


def download_csv(request, request_id):
    """Generates and serves a CSV file for the given request_id."""

    try:
        request_obj = ProcessingRequest.objects.get(request_id=request_id, status="COMPLETED")
    except ProcessingRequest.DoesNotExist:
        return HttpResponse("Request not found or not completed yet.", status=404)

    # Prepare response as CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="processed_images_{request_id}.csv"'

    writer = csv.writer(response)
    writer.writerow(["S. No.", "Product Name", "Input Image URLs", "Output Image URLs"])

    # Write data rows
    for product in request_obj.products.all():
        writer.writerow([
            product.serial_number,
            product.product_name,
            product.input_image_urls,
            product.output_image_urls
        ])

    return response
