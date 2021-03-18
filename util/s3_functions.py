import io
import platform
import re
from time import sleep
from PIL import Image
from selenium import webdriver
import boto3

class s3Functions():

    def __init__(self):
        #self.CHROME_DRIVER = self.get_chrome_driver()
        self.s3= boto3.client('s3')

    def __del__(self):
        self.CHROME_DRIVER.quit()

    def upload_image_from_url(self, bucket_name, url):
        """
        Fetch a snapshot of the application home page using Selenium

        Positional Arguments
        bucket_name:  s3 bucket name        
        url:  application URL

        Returns output filename, basically the meat of the URL,
        using '-' in place of non-alphnumeric chars, plus .png
        """
        file_name = re.sub(r'^https?://', '', url)
        file_name = re.sub(r'\W', '-', file_name) + '.png'
        #CHROME_DRIVER = self.get_chrome_driver()
        print('now doing chromedriver.get(',url,')')
        self.CHROME_DRIVER.get(url)
        print("now chrome driver has got the url")
        sleep(4)
        with io.BytesIO(self.CHROME_DRIVER.get_screenshot_as_png()) as f:
            print("now attempting to upload fileobj(file{},bucket{},file_name{})".format(f,bucket_name, file_name))
            self.s3.upload_fileobj(f, bucket_name, file_name)
        
        #CHROME_DRIVER.quit()
        return file_name

    def get_chrome_driver(self):
        """figure out which chromedriver to use from
        https://chromedriver.storage.googleapis.com/:
        linux64 or mac64
        """
        os_suffix = {'Linux':'linux64', 'Darwin':'mac64'}
        path = "../drivers/chromedriver87." + os_suffix.get(platform.system())
        # initiate selenium webdriver
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument("--incognito")
        option.add_argument('--hide-scrollbars')
        return webdriver.Chrome(path, options=option)

    def upload_image(self, bucket_name, unique_filename, f):
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(f, bucket_name, unique_filename)

    def get_image(self, bucket_name, file_name):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        image = bucket.Object(file_name)
        img_data = image.get().get('Body').read()
        return Image.open(io.BytesIO(img_data))
    
#    def get_image_list(self, bucket_name, file_list:list):
#        s3 = boto3.resource('s3')
#        bucket = s3.Bucket(bucket_name)
#        s3_list = [s3_file.key for s3_file in bucket.objects.all()]
#        return image_list

    def list_s3_objects(self, bucket_name):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        s3_list = [s3_file.key for s3_file in bucket.objects.all()]
        return s3_list

    def delete_image(self, bucket_name, file_name):
        s3 = boto3.resource('s3')
        obj = s3.Object(bucket_name, file_name)
        obj.delete()

    def create_presigned_url(self, bucket_name, file_name, expiration=60):
        """Generate a presigned URL to share an S3 object
        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        # Generate a presigned URL for the S3 object
        s3 = boto3.client('s3')
        try:
            response = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name,'Key': file_name}, ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None
        # The response contains the presigned URL
        return response
