#!/usr/bin/env python
"""
add-csv is used in forms for supervisors to add entire csv's to the db
THEY MUST follow the format
Load a set of application-dataset relationships in CSV form into a Neptune graph database
"""
import sys
sys.path.append("../")
import csv
from util import str_helper
from util.graph_db import GraphDB

def db_input_csv(fstring, orcid):
    graph = GraphDB()
    # initiate csv reader
    reader = [{k: v for k, v in row.items()} for row in csv.DictReader(fstring.splitlines(), skipinitialspace=True)]
    # loop through every line in csv file
    headers = reader[0].keys()
    print(headers)
    required_headers = {'topic', 'name', 'site', 'description', 'title', 'doi'}
    if not required_headers.issubset(headers):
        return False 
    for line in reader:
        print(line)
        if not 'type' in line.keys():
            line['type'] = 'unclassified'
        line['topic'] = str_helper.list_from_string(line['topic'])
        line['type'] = str_helper.list_from_string(line['type'])
        line['essential_variable'] = str_helper.list_from_string(line.get('essential_variable'))
        for index, t in enumerate(line['topic']):
            line['topic'][index] = t.strip()
            print(graph.add_topic(line['topic'][index]))
        if {'app_discoverer', 'app_verified', 'app_verifier'}.issubset(headers):
            graph.add_app(line, discoverer=line['app_discoverer'], verified=('true'==line['app_verified'].lower()), verifier=line['app_verifier'])
        else: 
            graph.add_app(line, discoverer=orcid, verified=True, verifier=orcid)
            #graph.add_app(line)
        graph.add_dataset(line)
        if {'discoverer', 'verifier', 'verified'}.issubset(headers):
            print('new line:\n', line)
            print('verifier:\n', line['verified'])
            graph.add_relationship(line['site'], line['doi'], discoverer=line['discoverer'], verified='true'==line['verified'].lower(), verifier=line['verifier'], annotation=line['annotation'])
        else:
            graph.add_relationship(line['site'], line['doi'], discoverer=orcid, verified=True, verifier=orcid)

    # counts vertices, used for troubleshooting purposes
    print(graph.get_vertex_count())
    print(graph.get_edge_count())
    return True

