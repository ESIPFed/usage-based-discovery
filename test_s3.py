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


        """
        Fetch a snapshot of the application home page using Selenium

        Positional Arguments
        driver:  selenium driver
        url:  application URL

        Returns output filename, basically the meat of the URL,
        using '-' in place of non-alphnumeric chars, plus .png
        """

        s3 = boto3.client('s3')
        url = "https://www.nasa.gov/"
        filename = re.sub(r'^https?://', '', url)
        filename = re.sub(r'\W', '-', filename) + '.png'
        self.s.upload_image_from_url(self.bucketName, url)
        try:
            s3.head_object(Bucket= self.bucketName, Key = filename)
        except ClientError:
            assert False
        assert True
        #We still have to remove the object from the s3 bucket after this test is done
        #does this fuction still run after an assert?

    def test_get_chrome_driver(self):
        pass

    def test_upload_image(self):
        s3 = boto3.client('s3')
        uniqueFilename = "this-is-a-unique-Filename"
        f = "test_s3.py"
        self.s.upload_image(bucketName, uniqueFilename, f)
        #upload a file from this directory and then remove it after the assert
        assert True
        try:
            s3.head_object(Bucket= self.bucketName, Key = uniqueFilename)
        except ClientError:
            assert False
        assert True

    def test_query_image(self):
        file_Name = "www-nasa-gov-.png"
        try:
            f = self.s.query_image(self.bucketName, file_Name)
        except:
            assert False
        assert True
    def test_list_s3_objects(self):
        x = self.s.list_s3_objects(self.bucketName)
        assert type(x)==list
