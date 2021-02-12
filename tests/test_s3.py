import sys
sys.path.append("../util")
import re
import requests
import time
import boto3
from botocore.errorfactory import ClientError
from s3_functions import s3Functions

class TestInit():

    def setup_method(self):
        self.s = s3Functions()
        self.bucket_name = "test-bucket-parth"
        self.s3 = boto3.client('s3')

    #have the funciton return the file name so you don't need to do that here
    def test_upload_image_from_url(self):
        url = "https://www.nasa.gov/"
        filename = re.sub(r'^https?://', '', url)
        filename = re.sub(r'\W', '-', filename) + '.png'

        #checks if object is in bucket when uploading
        self.s.upload_image_from_url(self.bucket_name, url)
        try:
            self.s3.head_object(Bucket= self.bucket_name, Key = filename)
        except ClientError as e:
            print("failed when checking if image was uploaded {}".format(e))
            assert False
        assert True
 
        #checks if object is not in bucket 
        self.s.delete_image(self.bucket_name, filename)
        try:
            self.s3.head_object(Bucket= self.bucket_name, Key = filename)
            
            print("failed when checking if image was deleted")
            assert False
        except ClientError:
            assert True
 
        #checks if object is in bucket
        self.s.upload_image_from_url(self.bucket_name, url)
        try:
            self.s3.head_object(Bucket= self.bucket_name, Key = filename)
        except ClientError as e: 
            print("failed when checking if image was uploaded 2nd time {}".format(e))
            assert False
        assert True

    def test_create_presigned_url(self):
        filename = "www-nasa-gov-.png"
        url = self.s.create_presigned_url(self.bucket_name, filename)
        assert requests.get(url).status_code == 200
        time.sleep(120)
        assert requests.get(url).status_code == 403

    def test_get_image(self):
        '''
        checks if www-nasa-gov-.png image is queried sucessfully and then removes it from s3
        '''
        filename = "www-nasa-gov-.png"
        try:
            f = self.s.get_image(self.bucket_name, filename)
        except error as e:
            print("failed while trying to get image from bucket, {}".format(e))
            assert False
        assert True
 
        #checks if object is not in bucket 
        self.s.delete_image(self.bucket_name, filename)
        try:
            self.s3.head_object(Bucket= self.bucket_name, Key = filename)
            print("failed while trying to delete object from bucket")
            assert False
        except ClientError:
            assert True

    def test_upload_image(self):
        '''
        uploads an image file from your directories and then removes it
        '''
        unique_filename = "test_s3.py"
        f = "test_s3.py"
        self.s.upload_image(self.bucket_name, unique_filename, f)
 
        try:
            self.s3.head_object(Bucket= self.bucket_name, Key = unique_filename)
        except ClientError as e:
            print("failed when checking if image was uploaded, {}".format(e))
            assert False
        self.s.delete_image(self.bucket_name, unique_filename)
        #checks if object is not in bucket 
        try:
            self.s3.head_object(Bucket= self.bucket_name, Key = unique_filename)
            print("failed because the object was not deleted from the bucket")
            assert False
        except ClientError:
            assert True
 
    def test_list_s3_objects(self):
        s3_list = self.s.list_s3_objects(self.bucket_name)
        assert type(s3_list)==list

    def test_delete_image(self):
        unique_filename = "test_s3.py"
       
