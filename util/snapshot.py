from s3_functions import s3Functions
from graph_db import GraphDB

s3 = s3Functions()
g = GraphDB()

NA = g.get_apps_without_screenshot()
for app in NA:
    name = app['name'][0]
    site = app['site'][0]
    print(name, site)
    screenshot = s3.upload_image_from_url('test-bucket-parth', site)
    g.update_app_property(name, 'screenshot', screenshot)
