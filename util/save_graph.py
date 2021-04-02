#!/usr/bin/env python
"""
load_graph.py
Load a set of application-dataset relationships in CSV form into a Neptune graph database
"""
import csv
from graph_db import GraphDB

def db_output_csv():
    header = ['topic', 'name', 'site', 'screenshot', 'description', 'publication', 'doi', 'title', 'discoverer', 'verifier', 'verified']
    graph = GraphDB()
    data = graph.get_data()
    with open("graph_snapshot.csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for link in data['links']:
            app_index = link['source']
            dataset_index = link['target']
            app = {}
            dataset = {}
            for node in data['nodes']:
                if node['id'] == app_index:
                    app = node
                if node['id'] == dataset_index:
                    dataset = node
            row = []
            row.append(app['topic'])
            row.append(app['name'][0])
            row.append(app['site'][0])
            row.append(app['screenshot'][0])
            row.append(app['description'][0])
            row.append(app['publication'][0])
            row.append(dataset['doi'][0])
            row.append(dataset['title'][0])
            row.append(link['discoverer'])
            row.append(link['verifier'])
            row.append(link['verified'])
            writer.writerow(row)
    file.close()

if __name__ == '__main__':
    db_output_csv()
