#!/usr/bin/env python
"""
Opposite of load_graph.py
Neptune DB to CSV format including all the edges and properties
"""
import csv
from graph_db import GraphDB

def db_output_csv():
    header = ['topic', 'type', 'name', 'site', 'screenshot', 'description', 'publication', 'app_discoverer', 'app_verified', 'app_verifier', 'doi', 'title', 'discoverer', 'verifier', 'verified', 'annotation']
    graph = GraphDB()
    data = graph.get_all_data()
    with open("graph_snapshot.csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for link in data['links']:
            if link['label'] == 'about': #skipping topic links
                continue
            print('link:\n', link)
            app_index = link['source']
            dataset_index = link['target']
            app = {}
            dataset = {}
            for node in data['nodes']:
                if node['id'] == app_index:
                    app = node
                if node['id'] == dataset_index:
                    dataset = node
            print('app:\n', app)
            print('datatset:\n', dataset)
            row = []
            row.append(graph.get_app_topics(app['site']))
            row.append(app['type'])
            row.append(app['essential_variable'])
            row.append(app['name'])
            row.append(app['site'])
            row.append(app['screenshot'])
            row.append(app['description'])
            row.append(app['publication'])
            row.append(app['discoverer'])
            row.append(app['verified'])
            row.append(app['verifier'])
            row.append(dataset['doi'])
            row.append(dataset['title'])
            row.append(link['discoverer'])
            row.append(link['verifier'])
            row.append(link['verified'])
            row.append(link['annotation'])
            writer.writerow(row)
    file.close()

if __name__ == '__main__':
    db_output_csv()
