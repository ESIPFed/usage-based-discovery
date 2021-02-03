import boto3
import io
from selenium import webdriver
import tempfile
import os
import platform
import sys
import re
from time import sleep
from PIL import Image
class s3Functions():

    def upload_image_from_url(self, bucket_Name, url):
        """
        Fetch a snapshot of the application home page using Selenium

        Positional Arguments
        driver:  selenium driver
        url:  application URL

        Returns output filename, basically the meat of the URL,
        using '-' in place of non-alphnumeric chars, plus .png
        """

        s3 = boto3.client('s3')
        CHROME_DRIVER = self.get_chrome_driver()
        filename = re.sub(r'^https?://', '', url)
        filename = re.sub(r'\W', '-', filename) + '.png'

        CHROME_DRIVER.get(url)
        sleep(2)
        with io.BytesIO(CHROME_DRIVER.get_screenshot_as_png()) as f:
            s3.upload_fileobj(f, bucket_Name, filename)


        return filename
    def get_chrome_driver(self):
        """figure out which chromedriver to use from
        https://chromedriver.storage.googleapis.com/:
        linux64 or mac64
        """
        os_suffix = {'Linux':'linux64', 'Darwin':'mac64'}

        path = "./chromedriver87." + os_suffix.get(platform.system())
        # initiate selenium webdriver
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        print(webdriver.Chrome(path, options=option))
        return webdriver.Chrome(path, options=option)
    
    def upload_image(self, bucket_Name, uniqueFilename, f):
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(f, bucket_Name, uniqueFilename) 
        


    def query_image(self, bucket_Name, file_Name):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_Name)
        image = bucket.Object(file_Name)
        img_data = image.get().get('Body').read()

        return Image.open(io.BytesIO(img_data))


    def list_s3_objects(self, bucket_Name):

        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket(bucket_Name)

        ls = [s3_file.key for s3_file in my_bucket.objects.all()]
        print(ls)
        return ls

    def delete_image(self, bucket_Name, file_Name):
        s3 = boto3.resource('s3')
        obj = s3.Object(bucket_Name, file_Name)
        obj.delete()



