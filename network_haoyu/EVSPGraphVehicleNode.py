import time
import network_haoyu.Graph as Graph

# 3 class vertex: trip vertex, origin/destination vertex, virtual vehicle vertex

class EVSPGraph(Graph.Graph):
    def __init__(self, time_granularity):
        super(EVSPGraph, self).__init__()
        # 时间粒度这里可能有问题，具体用到这个变量的时候再 check 一下
        self.time_granularity = time_granularity  # 15 min
        self.start_time = None
        self.start_time_str = None
        self.end_time = None
        self.end_time_str = None

    def addVertex(self, vertex_list):
        # 向 vertex_set 中添加 vertex
        vertex = EVSPVertex(vertex_id=vertex_list[0], vertex_attribute=vertex_list[1],
                           start_time_str=vertex_list[2], duration=vertex_list[3])
        self.vertex_set.append(vertex)
        return vertex

    def addTripVertex(self):
        pass

    def addDepotVertex(self, attribute):
        # 还没完成
        if attribute == 'origin':
            # [3, 'task', '2022-03-24 07:30:00', 45]
            vertex_list = [0, 'origin', self.start_time_str, 0]
            vertex_origin = self.addVertex(vertex_list=vertex_list)
        elif attribute == 'destination':
            vertex_list = []
            vertex_destination = self.addVertex(vertex_list=vertex_list)
            # add the edge compatible with vertex_destination
            self.addVertex()
        else:
            print('EVSPGraphVehicleNode.py -- addDepotVertex attribute input must be ‘origin’ or ‘destination’!')

    def addVirtualVehicleVertex(self):
        pass

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

    def constructGraph(self, vertex_info):
        # construct graph process:
        # 1. add origin vertex
        # 2. add virtual vehicle vertex
        # 3. add trip vertex
        # 4. add destination vertex

        pass



class EVSPVertex(Graph.Vertex):
    def __init__(self, vertex_id, vertex_attribute, start_time_str, duration):
        super(EVSPVertex, self).__init__()
        self.vertex_id = vertex_id
        self.vertex_attribute = vertex_attribute
        self.start_time_str = start_time_str
        self.start_time = int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
        self.duration = duration * 60


