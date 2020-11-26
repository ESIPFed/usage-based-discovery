from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection


def db():

   graph = Graph()

   remoteConn = DriverRemoteConnection('ws://neptunedbcluster-rmtayunusxcf.cluster-ro-cp6ppgqhmbet.us-east-1.neptune.amazonaws.com:8182/gremlin','g')
   g = graph.traversal().withRemote(remoteConn)

   return g