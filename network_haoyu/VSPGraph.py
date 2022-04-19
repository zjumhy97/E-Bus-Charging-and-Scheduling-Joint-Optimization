import time
import network_haoyu.Graph as Graph
import network_haoyu.DiGraph as DiGraph

class VSPGraph(DiGraph.DiGraph):
    def addVertex(self, vertex_list):
        # 向 vertex_set 中添加 vertex
        vertex = VSPVertex(vertex_id=vertex_list[0], vertex_attribute=vertex_list[1],
                           start_time=vertex_list[2], duration=vertex_list[3])
        self.vertex_set.append(vertex)
        return vertex

    def deleteVertex(self, vertex): # 还没实现
        # 获取与这个 vertex 相连的 edge, 还没实现
        removed_edge_set = set()

        # 从 vertex_set 中删除 vertex
        self.vertex_set.remove(vertex)
        # 从 edge_set 中删除相关的 edge
        self.edge_set = self.edge_set - removed_edge_set
        return 0

    def addEdge(self, vertex):
        # 根据时间判断，能否与已有节点创建有向边，有则添加
        vertex_set = self.vertex_set
        edge_id = len(self.edge_set)
        for i in vertex_set:
            if i.start_time + i.duration <= vertex.start_time:
                new_edge = self.edge_set.append(Graph.Edge(vertex_end1=i, vertex_end2=vertex, directed=True))
                i.edge_id_out.append(edge_id)
                vertex.edge_id_in.append(edge_id)
                edge_id += 1
            elif vertex.start_time + vertex.duration <= i.start_time:
                new_edge = self.edge_set.append(Graph.Edge(vertex_end1=vertex, vertex_end2=i, directed=True))
                vertex.edge_id_out.append(edge_id)
                i.edge_id_in.append(edge_id)
                edge_id += 1
            else:
                pass
        return 0


class VSPVertex(Graph.Vertex):
    def __init__(self, vertex_id, vertex_attribute, start_time, duration):
        super(VSPVertex, self).__init__()
        self.vertex_id = vertex_id
        self.vertex_attribute = vertex_attribute
        self.start_time_str = start_time
        self.start_time = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S")))
        self.duration = duration * 60


