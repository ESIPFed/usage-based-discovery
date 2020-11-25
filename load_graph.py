
from __future__  import print_function  # Python 2/3 compatibility

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

import csv
from gremlin_python.process.traversal import Bindings


def db():

   graph = Graph()

   remoteConn = DriverRemoteConnection('ws://localhost:8182/gremlin','g')
   g = graph.traversal().withRemote(remoteConn)

   # load graph

   g.V().drop().iterate() # clear graph


   with open('output.csv', 'r') as file: # load csv file
      reader = csv.DictReader(file)
      
      for line in reader:
         names = g.V().name.toList()
         titles = g.V().title.toList()

         if line['name'] not in names:    # eventually add description and query link as property
            v1 = g.addV('application').property('topic', line['topic']).property('name', line['name']) \
               .property('site', line['site']).property('screenshot', line['screenshot']).property('publication', line['publication']).next()
         else:
            v1 = g.V().has('application', 'name', line['name']).limit(1)
         
         if line['title'] not in titles:
            v2 = g.addV('dataset').property('doi', line['doi']).property('title', line['title']).next()
         else:
            v2 = g.V().has('dataset', 'title', line['title']).limit(1)
         
         g.addE('uses').from_(v1).to(v2).iterate()

      '''
         v1 = g.addV('application').property('topic', line['topic']).property('name', line['name']) \
               .property('site', line['site']).property('screenshot', line['screenshot']).property('publication', line['publication']).next()
         v2 = g.addV('dataset').property('doi', line['doi']).property('title', line['title']).next()
         g.V(Bindings.of('id',v1)).addE('uses').to(v2).iterate()
      '''


   msg = 'Vertices count: ', g.V().count().next() # count vertices
   # print(msg)

   # remoteConn.close()
   
   return g
