import io
import platform
import re
from time import sleep
from selenium import webdriver
import boto3
import os
import pathlib
from flask import url_for

class s3Functions():

    def __init__(self):
        if os.environ.get('FLASK_ENV') != 'development':
            self.s3= boto3.client('s3')

    def __del__(self):
        pass

    def rename_file(self, bucket_name, old_path, new_path):
        if os.environ.get('FLASK_ENV') == 'development':
            return
        s3_resource = boto3.resource('s3')
        s3_resource.Object(bucket_name, new_path).copy_from(CopySource=f'{bucket_name}/{old_path}')
        s3_resource.Object(bucket_name, old_path).delete()

    def upload_image_from_url(self, bucket_name, url, CHROME_DRIVER):
        """
        Fetch a snapshot of the application home page using Selenium

        Positional Arguments
        bucket_name:  s3 bucket name        
        url:  application URL

        Returns output filename, basically the meat of the URL,
        using '-' in place of non-alphnumeric chars, plus .png
        """
        if os.environ.get('FLASK_ENV') == 'development':
            return
        file_name = re.sub(r'^https?://', '', url)
        file_name = re.sub(r'\W', '-', file_name) + '.png'
        print('now doing chromedriver.get(',url,')')
        CHROME_DRIVER.get(url)
        print("now chrome driver has got the url")
        sleep(4)
        with io.BytesIO(CHROME_DRIVER.get_screenshot_as_png()) as f:
            print("now attempting to upload fileobj(file{},bucket{},file_name{})".format(f,bucket_name, file_name))
            self.s3.upload_fileobj(f, bucket_name, file_name)
        return file_name

    def get_chrome_driver(self):
        """figure out which chromedriver to use from
        https://chromedriver.storage.googleapis.com/:
        linux64 or mac64
        """
        if os.environ.get('FLASK_ENV') == 'development':
            return
        os_suffix = {'Linux':'linux64', 'Darwin':'mac64'}
        path = "../drivers/chromedriver89." + os_suffix.get(platform.system())
        # initiate selenium webdriver
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument("--incognito")
        option.add_argument('--hide-scrollbars')
        return webdriver.Chrome(path, options=option)

    def upload_image(self, bucket_name, unique_filename, f):
        if os.environ.get('FLASK_ENV') == 'development':
            return
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(f, bucket_name, unique_filename)

    def upload_image_obj(self, bucket_name, unique_filename, f):
        if os.environ.get('FLASK_ENV') == 'development':
            return
        s3 = boto3.resource('s3')
        s3.meta.client.upload_fileobj(f, bucket_name, unique_filename)

    def get_file_local(self, file_name):
        with open(pathlib.Path.cwd() / file_name, mode='r') as f:
            return f.read()

    def get_file(self, bucket_name, file_name):
        if os.environ.get('FLASK_ENV') == 'development':
            return self.get_file_local(file_name)
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        f = bucket.Object(file_name)
        file_data = f.get().get('Body').read()
        return file_data

#    def get_image_list(self, bucket_name, file_list:list):
#        s3 = boto3.resource('s3')
#        bucket = s3.Bucket(bucket_name)
#        s3_list = [s3_file.key for s3_file in bucket.objects.all()]
#        return image_list

    def list_s3_objects(self, bucket_name):
        if os.environ.get('FLASK_ENV') == 'development':
            return
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        s3_list = [s3_file.key for s3_file in bucket.objects.all()]
        return s3_list

    def delete_image(self, bucket_name, file_name):
        if os.environ.get('FLASK_ENV') == 'development':
            return
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
        if os.environ.get('FLASK_ENV') == 'development':
            return url_for('static', filename=file_name)
        # Generate a presigned URL for the S3 object
        s3 = boto3.client('s3')
        try:
            response = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name,'Key': file_name}, ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None
        # The response contains the presigned URL
        return response
