import time
import network_haoyu.Graph as Graph

# 3 class vertex: trip vertex, origin/destination vertex, virtual vehicle vertex

class EVSPGraph(Graph.Graph):
    def __init__(self, time_granularity, soc_ev, trip_info, start_time, end_time):
        super(EVSPGraph, self).__init__()
        # 时间粒度这里可能有问题，具体用到这个变量的时候再 check 一下
        # time_granularity > 1
        self.time_granularity = time_granularity  # 15 min
        self.soc_ev = soc_ev
        self.vehicle_num = len(soc_ev)
        self.start_time = start_time
        self.start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        self.end_time = end_time
        self.end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
        self.pull_out_edge_list = []
        self.trip_info = trip_info
        self.edge_dict = {}

    def add_vertex(self, id, attribute, start_time_str, duration):
        # 向 vertex_set 中添加 vertex
        vertex = EVSPVertex(vertex_id=id, vertex_attribute=attribute, start_time_str=start_time_str, duration=duration)
        self.vertex_set.append(vertex)
        self.update()
        return vertex

    def add_trip_vertex(self):
        # [3, 'task', '2022-03-24 07:30:00', 45]
        trip_number = len(self.trip_info)
        for i in range(1, trip_number+1):
            trip = self.trip_info['trip' + str(i)]
            vertex = self.add_vertex(id=trip['trip_id'] + self.vehicle_num, attribute=trip['attribute'],
                                     start_time_str=trip['start_time_str'], duration=trip['duration'])
            vertex.energy_consumption = trip['energy_consumption']
            self.add_edge(vertex=vertex, attribute='normal')
        return 0

    def add_depot_vertex(self, attribute):
        # depot vertex duration > 0, here we set the duration to 1 min
        if attribute == 'origin':
            # [3, 'task', '2022-03-24 07:30:00', 45]
            vertex_origin = self.add_vertex(id=0, attribute='origin',
                                            start_time_str=self.start_time_str, duration=1)
        elif attribute == 'destination':
            # vertex_list = [900000, 'destination', self.end_time_str, 1]
            self.update()
            vertex_destination = self.add_vertex(id=self.vertex_size,attribute='destination',
                                                start_time_str=self.end_time_str, duration=1)
            # add the edge compatible with vertex_destination
            self.add_edge(vertex=vertex_destination, attribute='pull in')
        else:
            print('EVSPGraphVehicleNode.py -- addDepotVertex attribute input must be ‘origin’ or ‘destination’!')
        self.update()
        return 0

    def add_virtual_vehicle_vertex(self, soc_ev):
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
                # vertex_list = [i+100001, vehicle, start_time_str, 1]
                vertex_vehicle = self.add_vertex(id=i+1, attribute=vehicle, start_time_str=start_time_str,
                                                 duration=1)
                vertex_vehicle.soc = soc
                i += 1
                self.add_edge(vertex=vertex_vehicle, attribute='pull out')
            # update the pull_out_edge_list of this graph
            edge_id = len(self.edge_set)
            self.pull_out_edge_list.extend([i for i in range(edge_id)])
        else:
            print('EVSPGraphVehicleNode.py -- addVirtualVehicleVertex error!')
        self.update()
        return 0

    def add_edge(self, vertex, attribute):
        # 根据时间判断，能否与已有节点创建有向边，add time compatible edge
        vertex_set = self.vertex_set
        edge_id = len(self.edge_set)
        for i in vertex_set:
            if i.start_time + i.duration <= vertex.start_time:
                edge = self.edge_set.append(EVSPEdge(edge_id=edge_id, attribute=attribute, end1=i, end2=vertex))
                i.edge_id_out.append(edge_id)
                vertex.edge_id_in.append(edge_id)
                self.edge_dict[(i.vertex_id, vertex.vertex_id)] = edge_id
                edge_id += 1
            elif vertex.start_time + vertex.duration <= i.start_time:
                edge = self.edge_set.append(EVSPEdge(edge_id=edge_id, attribute=attribute, end1=vertex, end2=i))
                vertex.edge_id_out.append(edge_id)
                i.edge_id_in.append(edge_id)
                self.edge_dict[(vertex.vertex_id, i.vertex_id)] = edge_id
                edge_id += 1
            else:
                pass
        self.update()
        return 0

    def construct_graph(self):
        # construct graph process:
        # 1. add origin vertex
        self.add_depot_vertex(attribute='origin')
        # 2. add virtual vehicle vertex
        self.add_virtual_vehicle_vertex(soc_ev=self.soc_ev)
        # 3. add trip vertex
        self.add_trip_vertex()
        # 4. add destination vertex
        self.add_depot_vertex(attribute='destination')
        return 0


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
        self.energy_consumption = None

class EVSPEdge(Graph.Edge):
    def __init__(self, edge_id, attribute, end1, end2, directed=True, weight=1):
        super(EVSPEdge, self).__init__(vertex_end1=end1, vertex_end2=end2, directed=directed, weight=weight)
        self.edge_id = edge_id
        self.attribute = attribute # attribute: pull out, normal, pull in
