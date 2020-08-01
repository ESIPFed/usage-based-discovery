from py2neo import Graph, Node, Relationship
import csv


def db():

    graph = Graph("bolt://hobby-fcaccojbajhegbkelpidkifl.dbs.graphenedb.com:24787", auth=("neo4j", "b.RsWIZv4ntCee.7TYDxTHsycMuOMg9"), secure=True)     

    return graph





