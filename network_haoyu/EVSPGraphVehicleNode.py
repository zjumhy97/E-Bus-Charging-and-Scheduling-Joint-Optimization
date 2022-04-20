import time
import network_haoyu.Graph as Graph

# 3 class vertex: trip vertex, origin/destination vertex, virtual vehicle vertex

class EVSPGraph(Graph.Graph):
    def __init__(self, time_granularity, soc_ev):
        super(EVSPGraph, self).__init__()
        # 时间粒度这里可能有问题，具体用到这个变量的时候再 check 一下
        # time_granularity > 1
        self.time_granularity = time_granularity  # 15 min
        self.soc_ev = soc_ev
        self.vehicle_num = len(soc_ev)
        self.start_time = None
        self.start_time_str = None
        self.end_time = None
        self.end_time_str = None
        self.pull_out_edge_list = []

    def addVertex(self, vertex_list):
        # 向 vertex_set 中添加 vertex
        vertex = EVSPVertex(vertex_id=vertex_list[0], vertex_attribute=vertex_list[1],
                           start_time_str=vertex_list[2], duration=vertex_list[3])
        self.vertex_set.append(vertex)
        return vertex

    def addTripVertex(self):
        # 还没完成
        vertex_list = []
        vertex = self.addVertex(vertex_list=vertex_list)
        self.addEdge(vertex=vertex, attribute='trip')
        self.update()
        return 0

    def addDepotVertex(self, attribute):
        # depot vertex duration > 0, here we set the duration to 1 min
        if attribute == 'origin':
            # [3, 'task', '2022-03-24 07:30:00', 45]
            vertex_list = [0, 'origin', self.start_time_str, 1]
            vertex_origin = self.addVertex(vertex_list=vertex_list)
        elif attribute == 'destination':
            vertex_list = [900000, 'destination', self.end_time_str, 1]
            vertex_destination = self.addVertex(vertex_list=vertex_list)
            # add the edge compatible with vertex_destination
            self.addEdge(vertex=vertex_destination, attribute='pull in')
        else:
            print('EVSPGraphVehicleNode.py -- addDepotVertex attribute input must be ‘origin’ or ‘destination’!')
        self.update()
        return 0

    def addVirtualVehicleVertex(self, soc_ev):
        # 除了添加 vehicle vertex， 也添加了 pull out edge
        # soc_ev = {'粤B12345':100, '粤B23456':100, '粤B34567':100, '粤B45678':100}
        # 添加 virtual vehicle node 需要添加 ev 的 soc
        vertex_num = len(self.vertex_set)
        if vertex_num == 0:
            print('EVSPGraphVehicleNode.py -- addVirtualVehicleVertex Please add origin vertex first!')
        elif vertex_num == 1:
            vertex_origin = self.vertex_set[0]
            i = 0
            for vehicle, soc in soc_ev.items():
                # 还没完成
                # [3, 'task', '2022-03-24 07:30:00', 45]
                start_time = self.start_time + vertex_origin.duration
                start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
                vertex_list = [i+100001, vehicle, start_time_str, 1]
                vertex_vehicle = self.addVertex(vertex_list=vertex_list)
                vertex_vehicle.soc = soc
                i += 1
                self.addEdge(vertex=vertex_vehicle, attribute='pull out')
            # update the pull_out_edge_list of this graph
            edge_id = len(self.edge_set)
            self.pull_out_edge_list.extend([i for i in range(edge_id)])
        else:
            print('EVSPGraphVehicleNode.py -- addVirtualVehicleVertex error!')
        self.update()
        return 0

    def addEdge(self, vertex, attribute):
        # 根据时间判断，能否与已有节点创建有向边，add time compatible edge
        vertex_set = self.vertex_set
        edge_id = len(self.edge_set)
        for i in vertex_set:
            if i.start_time + i.duration <= vertex.start_time:
                edge = self.edge_set.append(EVSPEdge(edge_id=edge_id, attribute=attribute, end1=i, end2=vertex))
                i.edge_id_out.append(edge_id)
                vertex.edge_id_in.append(edge_id)
                edge_id += 1
            elif vertex.start_time + vertex.duration <= i.start_time:
                edge = self.edge_set.append(EVSPEdge(edge_id=edge_id, attribute=attribute, end1=vertex, end2=i))
                vertex.edge_id_out.append(edge_id)
                i.edge_id_in.append(edge_id)
                edge_id += 1
            else:
                pass
        self.update()
        return 0

    def constructGraph(self, vertex_info):
        # construct graph process:
        # 1. add origin vertex
        self.addDepotVertex(attribute='origin')
        # 2. add virtual vehicle vertex
        self.addVirtualVehicleVertex(soc_ev=self.soc_ev)
        # 3. add trip vertex
        self.addTripVertex()
        # 4. add destination vertex
        self.addDepotVertex(attribute='destination')
        pass



class EVSPVertex(Graph.Vertex):
    def __init__(self, vertex_id, vertex_attribute, start_time_str, duration):
        super(EVSPVertex, self).__init__()
        self.vertex_id = vertex_id
        self.vertex_attribute = vertex_attribute
        self.start_time_str = start_time_str
        self.start_time = int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
        self.duration = duration * 60
        # 设置为 None 是否合理？
        self.soc = None

class EVSPEdge(Graph.Edge):
    def __init__(self, edge_id, attribute, end1, end2, directed=True, weight=0):
        super(EVSPEdge, self).__init__(vertex_end1=end1, vertex_end2=end2, directed=directed, weight=weight)
        self.edge_id = edge_id
        self.attribute = attribute # attribute: pull out, trip, pull in
