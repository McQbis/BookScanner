from celery import shared_task
from celery.exceptions import TimeoutError
from django.core.files.base import ContentFile
from .models import EncryptedPhoto
from .utils import get_user_key
from .image_processing import ImageProcessing

image_processing_gpu = ImageProcessing(device='cuda')
image_processing_cpu = ImageProcessing(device='cpu')


def _run_image_processing(user_id, photo_id, image_bytes, processor):
    """ Run the image processing task with the specified processor."""
    processed = processor(image_bytes)

    photo = EncryptedPhoto.objects.get(id=photo_id)
    fernet = get_user_key(user_id)
    encrypted_data = fernet.encrypt(processed)
    encrypted_file = ContentFile(encrypted_data)

    filename = f"user_{user_id}_{photo_id}.enc"
    photo.file.save(filename, encrypted_file)
    photo.save()


@shared_task(queue='gpu')
def _process_image_gpu(user_id, photo_id, image_bytes):
    """ Process the image using GPU. """
    _run_image_processing(user_id, photo_id, image_bytes, image_processing_gpu)
    return "processed_by_gpu"


@shared_task(queue='cpu')
def _process_image_cpu(user_id, photo_id, image_bytes):
    """ Process the image using CPU. """
    _run_image_processing(user_id, photo_id, image_bytes, image_processing_cpu)
    return "processed_by_cpu"


@shared_task
def process_and_store_image(user_id, photo_id, image_bytes):
    """
    Process the image using GPU if available, otherwise fallback to CPU.
    This task will try to process the image with the GPU first, and if it times out
    or fails, it will fall back to processing with the CPU.

    Args:
        user_id (int): The ID of the user who uploaded the photo.
        photo_id (int): The ID of the photo to be processed.
        image_bytes (bytes): The raw bytes of the uploaded image.

    Returns:
        str: A message indicating whether the image was processed by GPU or CPU.
    """
    try:
        result = _process_image_gpu.apply_async(
            args=(user_id, photo_id, image_bytes),
            queue='gpu'
        )
        return result.get(timeout=5)
    except TimeoutError:
        return _process_image_cpu.delay(user_id, photo_id, image_bytes)