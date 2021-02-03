import pytest
from s3_functions import s3Functions
import boto3
import re
from botocore.errorfactory import ClientError
bucketName = "test-bucket-parth"
class TestInit():

    def setup_method(self):
        self.s = s3Functions()
        self.bucketName = "test-bucket-parth"
    
    def test_upload_image_from_url(self):
        s3 = boto3.client('s3')
        url = "https://www.nasa.gov/"
        filename = re.sub(r'^https?://', '', url)
        filename = re.sub(r'\W', '-', filename) + '.png'
        
        #checks if object is in bucket when uploading
        self.s.upload_image_from_url(self.bucketName, url)
        try:
            s3.head_object(Bucket= self.bucketName, Key = filename)
        except ClientError:
            assert False
        assert True
        
        #checks if object is not in bucket        
        self.s.delete_image(self.bucketName, filename)
        try:
            s3.head_object(Bucket= self.bucketName, Key = filename)
            assert False
        except ClientError:
            assert True
         
        #checks if object is in bucket
        self.s.upload_image_from_url(self.bucketName, url)
        try:
            s3.head_object(Bucket= self.bucketName, Key = filename)
        except ClientError:
            assert False
        assert True
        
    def test_query_image(self):
        '''
        checks if www-nasa-gov-.png image is queried sucessfully and then removes it from s3
        '''
        s3 = boto3.client('s3')
        filename = "www-nasa-gov-.png"
        try:
            f = self.s.query_image(self.bucketName, filename)
        except:
            assert False
        assert True       
            
        #checks if object is not in bucket        
        self.s.delete_image(self.bucketName, filename)
        try:
            s3.head_object(Bucket= self.bucketName, Key = filename)
            assert False
        except ClientError:
            assert True
    
    def test_get_chrome_driver(self):
        pass

    def test_upload_image(self):
        '''
        uploads an image file from your directories and then removes it
        '''
        s3 = boto3.client('s3')
        uniqueFilename = "test_s3.py"
        f = "test_s3.py"
        self.s.upload_image(bucketName, uniqueFilename, f)
        
        try:
            s3.head_object(Bucket= self.bucketName, Key = uniqueFilename)
        except ClientError:
            assert False
        
        self.s.delete_image(self.bucketName, uniqueFilename)
        #checks if object is not in bucket        
        try:
            s3.head_object(Bucket= self.bucketName, Key = uniqueFilename)
            assert False
        except ClientError:
            assert True
 
    def test_list_s3_objects(self):
        x = self.s.list_s3_objects(self.bucketName)
        assert type(x)==list
