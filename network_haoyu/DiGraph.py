import time
from abc import abstractmethod
import network_haoyu as nwk
import network_haoyu.Graph as Graph

class DiGraph(Graph.Graph):
    def constructGraph(self, vertex_info):
        for i in range(len(vertex_info)):
            vertex = self.addVertex(vertex_info[i])
            self.addEdge(vertex)

    # @abstractmethod
    def addVertex(self, vertex_list):
        raise NotImplementedError

    def deleteVertex(self, vertex): # 还没实现
        pass

    def addEdge(self, vertex):
        pass





