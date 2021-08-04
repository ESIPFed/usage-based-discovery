from werkzeug.datastructures import ImmutableMultiDict
import io

def extract_datasets_from_form(f):
    sets = []
    list_of_datasets = []
    list_of_DOIs = []
    for key,value in f.items(): 
        if key[-1].isdigit():
            if key[:4] =="Data":
                list_of_datasets.append(value)
            if key[:4] =="DOI_":
                list_of_DOIs.append(value)
    for Dataset_name, DOI in zip(list_of_datasets, list_of_DOIs):
        sets.append({'title': [Dataset_name], 'doi': [DOI]})
    return sets

class MockData:

    @staticmethod
    def get(type, orcid, is_edit=False):
        form = MockData.buildForm(type, is_edit)
        return dict(
            form = form,
            app = MockData.buildApp(form, orcid),
            datasets = extract_datasets_from_form(form)
        )

    @staticmethod
    def buildForm(type, is_edit=False):
        d_items = [
            ('Type[]', type), 
            ('Application_Name', 'ABoVE -  Burn Severity, Fire Progression, Landcover and Field Data, NWT, Canada, 2014'), 
            ('Publication_Link', 'https://daac.ornl.gov/ABOVE/guides/Wildfires_2014_NWT_Canada.html'), 
            ('Topic[]', 'Fires'), 
            ('Topic[]', 'Custom Topic 1'), 
            ('Topic[]', 'Custom Topic 2'), 
            ('custom_topic', ''), 
            ('essential_variable', 'Groundwater'), 
            ('essential_variable', 'Lakes'), 
            ('description', 'The fire progression maps were made using an algorithm that enabled an assessment of wildfire progression rates at a daily time scale.'), 
            ('site', 'http://site.com'), 
            ('Dataset_Name_1', 'ABoVE: Burn Severity, Fire Progression, Landcover and Field Data, NWT, Canada, 2014'), 
            ('DOI_1', 'https://doi.org/10.3334/ORNLDAAC/1307'), 
            ('Dataset_Name_2', 'DS2'), 
            ('DOI_2', 'http://data.com'),
            ('image_file', (io.BytesIO(b"abcdef"), 'test.jpg'))
        ]
        if is_edit:
            d_items.append(('prev_app_site', 'http://site.com'))
        return ImmutableMultiDict(d_items)

    @staticmethod
    def buildApp(form, orcid):
        app = {
            'type': form.getlist('Type[]'),
            'name': form.getlist('Application_Name'), 
            'essential_variable': form.getlist('essential_variable'), 
            'description': form.getlist('description'), 
            'site': form.getlist('site'),  
            'verifier': [orcid], 
            'verified': [True], 
            'discoverer': [orcid]
        }
        if form['Type[]'] == 'Software':
            app['screenshot'] = [form.get('image_file')[1]]
        if form['Type[]'] == 'Software':
            app['publication'] = form.getlist('Publication_Link')
        return app