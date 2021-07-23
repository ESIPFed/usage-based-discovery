from PIL import Image
import io
import os
from util import s3_functions

def resize_image_file(image_file, dims):
    pil_image = Image.open(image_file)
    pil_image.thumbnail(dims)
    new_file = io.BytesIO()
    pil_image.save(new_file, format=pil_image.format, optimize=True)
    new_file.seek(0)

    return new_file

def upload_thumbnail(request, dims, img_path=None):
    if 'image_file' in request.files.keys() and request.files['image_file'].filename != '':
        print(f"Request contains image { request.files['image_file'] }")
        file_name = request.files['image_file'].filename
        if img_path:
            file_name = img_path
        resized_image = resize_image_file(request.files['image_file'], dims)
        s3 = s3_functions.s3Functions()
        s3.upload_image_obj(os.environ.get('S3_BUCKET'), file_name, resized_image)
        return file_name
    else:
        print('Request is missing image')
        return None

    
