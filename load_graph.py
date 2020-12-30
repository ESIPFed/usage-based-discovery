
from __future__  import print_function  # Python 2/3 compatibility

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

import csv
from gremlin_python.process.traversal import Bindings


def db():

   # initiate connection
   graph = Graph()
   remoteConn = DriverRemoteConnection('wss://neptunedbinstance-4lxhmnqeyz6s.copyeo4gkrow.us-west-1.neptune.amazonaws.com:8182/gremlin','g')
   g = graph.traversal().withRemote(remoteConn)
   
   # start loading graph
   
   empty = False
   # clear graph
   try:
       g.V().drop().iterate() 
   except:
       empty = True
       print("No existing graphs to clear")
       names = []
       titles = []
   
   # load csv file
   with open('algo-output.csv', 'r') as file: 
      
      # initiate csv reader
      reader = csv.DictReader(file)
      
      # loop through every line in csv file
      for line in reader:
         # initiate new graph connection -- not entirely necessary, used for troubleshooting purposes
         g = graph.traversal().withRemote(remoteConn)

         # generates a list of existing applications and datasets to avoid duplicates
         if not empty:
            names = g.V().name.toList()
            titles = g.V().title.toList()

         # this conditional checks for application duplicates
         if line['name'] not in names:    
            # if application is not yet in database, add it
            v1 = g.addV('application').property('topic', line['topic']).property('name', line['name']) \
               .property('site', line['site']).property('screenshot', line['screenshot']) \
               .property('publication', line['publication']).property('description', line['description']).next()
         else:
            # else, get existing application vertex
            v1 = g.V().has('application', 'name', line['name']).limit(1)
         
         # this conditional checks for dataset duplicates
         if line['title'] not in titles:
            # if dataset is not yet in database, add it
            v2 = g.addV('dataset').property('doi', line['doi']).property('title', line['title']).next()
         else:
            # else, get existing dataset vertex
            v2 = g.V().has('dataset', 'title', line['title']).limit(1)
         
         # add edge between application and dataset vertices
         g.addE('uses').from_(v1).to(v2).iterate()


   # old way of loading that did not account for duplicates
   '''
      v1 = g.addV('application').property('topic', line['topic']).property('name', line['name']) \               .property('site', line['site']).property('screenshot', line['screenshot']).property('publication', line['publication']).next()
      v2 = g.addV('dataset').property('doi', line['doi']).property('title', line['title']).next()
      g.V(Bindings.of('id',v1)).addE('uses').to(v2).iterate()
   '''

   # counts vertices, used for troubleshooting purposes
   msg = 'Vertices count: ', g.V().count().next() 
   # print(msg)

   # close connection
   # remoteConn.close()
   
   return g


# calling the function to load the database
db()







# The following code is used solely for troubleshooting purposes. 
# You can ignore/delete/archive this portion 

def test():

   graph = Graph()

   remoteConn = DriverRemoteConnection('ws://localhost:8182/gremlin','g')
   g = graph.traversal().withRemote(remoteConn)
   
   count = 0

   # goes through all applications
   for s in g.V().name.toList():
      print(s)
      
      print("\n")

   print("DATASETS\n")

   # goes through all datasets
   for d in g.V().title.toList():
      print(d)
      count += 1
      print("\n")

   # prints number of datasets in database
   print(count)

   # load csv file
   with open('algo-output.csv', 'r') as file: 
      reader = csv.DictReader(file)
      
      datasets = set()
      for line in reader:
         datasets.add(line['title'])
      
      # prints how many distinct datasets exist in specified csv file
      print(len(datasets))


# calling the function for troubleshooting purposes
# test()
