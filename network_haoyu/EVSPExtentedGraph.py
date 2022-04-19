import time
import math
import network_haoyu.DiGraph as DiGraph
import network_haoyu.Graph as Graph

# Extended graph is a 3-dimension Graph
# task, time, SOC -- x, y, z
# each task is a plane

class EVSPExtentedGraph(Graph.Graph):
    def __init__(self, time_granularity, soc_level_number, soc_level_lower_limit, battery_capacity, charger_number):
        super(EVSPExtentedGraph, self).__init__()
        # 时间粒度这里可能有问题，具体用到这个变量的时候再 check 一下
        self.time_granularity = time_granularity # 15 min
        self.soc_level_number = soc_level_number # 10 levels, from 0 to 10
        self.soc_granularity = 100 / soc_level_number # 100 / 10 = 10
        self.soc_level_lower_limit = soc_level_lower_limit # 1 is 10% of soc
        self.battery_capacity = battery_capacity
        self.coordinate_list = []
        self.coordinate_code_list = []
        self.coordinate_code_dict = {}
        self.start_time = None
        self.start_time_str = None
        self.end_time = None
        self.end_time_str = None
        self.plane_number = 0
        self.trip_in_vertex_list = []
        self.charging_edge_set = None
        self.charger_number = charger_number

    def constructGraph(self, trip_info):
        for i in range(len(trip_info)):
            trip = Trip(trip_id=trip_info[i][0], attribute=trip_info[i][1],
                               start_time_str=trip_info[i][2], duration=trip_info[i][3],
                               energy_consumption_level=trip_info[i][4])
            if i == 0:
                self.addPlaneOrigin(trip_origin=trip)
            else:
                self.addPlaneTask(trip_task=trip)
        self.addPlaneDestination()

    def addVertex(self, vertex_list):
        vertex_id = len(self.vertex_set)
        vertex = Vertex(vertex_id=vertex_id, coordinate=vertex_list[0], start_time_str=vertex_list[1],
                        duration=vertex_list[2])
        self.vertex_set.append(vertex)
        # 为了后续查找有没有合适的 coordinate 以创建 switch edge，这里建立 coordinate_list
        self.coordinate_list.append(vertex.coordinate)
        self.coordinate_code_list.append(vertex.coordinate_code)
        self.coordinate_code_dict[vertex.coordinate_code] = vertex_id
        return vertex

    def addEdge(self, edge_list):
        # addEdge 可以一个一个添加边，需不需要再弄个一列一列添加边的？
        edge_id = len(self.edge_set)
        edge = Edge(edge_id=edge_id, attribute=edge_list[0], end1=edge_list[1], end2=edge_list[2])
        start = edge_list[1]
        end = edge_list[2]
        start.edge_id_out.append(edge.edge_id)
        end.edge_id_in.append(edge.edge_id)
        self.edge_set.append(edge)
        if edge.attribute == 'charging':
            self.charging_edge_set[int((start.start_time - self.start_time) / self.time_granularity / 60)].append(edge_id)
        return edge

    def addPlaneOrigin(self, trip_origin,):
        # 添加初始起点平面
        start_time = trip_origin.start_time
        start_time_str = trip_origin.start_time_str
        self.start_time = trip_origin.start_time
        self.end_time = self.start_time + 86400
        self.start_time_str = start_time_str
        self.end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.end_time))
        self.charging_edge_set = [[] for _ in range(int((self.end_time - self.start_time)/self.time_granularity/60))]

        # 添加第一个顶点
        vertex_list = [(0, start_time, self.soc_level_number), start_time_str, self.time_granularity]
        vertex_origin = self.addVertex(vertex_list=vertex_list)
        # 循环添加后续的顶点以及第一个顶点与这些顶点的边
        # start_time_copy = start_time
        time_index = start_time
        while time_index < self.end_time:
            # start_time 需要更新 + 15min
            start_time += self.time_granularity * 60
            start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
            vertex_list = [(0, start_time, self.soc_level_number), start_time_str, self.time_granularity]
            vertex_new = self.addVertex(vertex_list)
            edge_list = ['waiting', vertex_origin, vertex_new]
            self.addEdge(edge_list=edge_list)
            time_index = start_time
        self.plane_number += 1
        self.trip_in_vertex_list.append(['empty'])
        return 1

    def addPlaneTask(self, trip_task):
        # 第一列顶点的时间
        column_1_time = trip_task.start_time
        column_1_time_str = trip_task.start_time_str
        trip_in_vertex_list = []

        timer_2 = time.time()
        timer_a = 0

        # step 1: 添加第一列顶点 重点是表示 SOC 从 10 到 4
        for soc_level in range(self.soc_level_number, self.soc_level_lower_limit +
                         trip_task.energy_consumption_level - 1, -1): # (10, 1 + 3 - 1, -1) : 10 --> 4
            vertex_list = [(trip_task.trip_id, column_1_time, soc_level), column_1_time_str, trip_task.duration]
            vertex = self.addVertex(vertex_list=vertex_list)
            # 将第一列的 vertex 存到一个 list 中
            trip_in_vertex_list.append(vertex)
            # 添加和之前 plane 相连接的边

            timer_0 = time.time()
            for i in range(trip_task.trip_id):
                vertex_previous_coordinate_code = trip_task.start_time * 10000000 + i * 1000 + soc_level
                if vertex_previous_coordinate_code in self.coordinate_code_dict:
                # if vertex_previous_coordinate_code in self.coordinate_code_list:
                # if (i, column_1_time, soc_level) in self.coordinate_list:
                    # 如果前面的平面内存在顶点的坐标为 (i, start_time, soc_level)，则建立这条边
                    # vertex_previous_id = self.coordinate_list.index((i, column_1_time, soc_level)))
                    # vertex_previous_id = self.coordinate_code_list.index(vertex_previous_coordinate_code)
                    vertex_previous_id = self.coordinate_code_dict[vertex_previous_coordinate_code]
                    edge_list = ['switch', self.vertex_set[vertex_previous_id], vertex]
                    self.addEdge(edge_list=edge_list)
            timer_1 = time.time()
            timer_a += timer_1 - timer_0

        # step 2: 添加第二列顶点
        column_2_time = column_1_time + trip_task.duration * 60
        column_2_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(column_2_time))
        for soc_level in range(self.soc_level_number - trip_task.energy_consumption_level,
                               self.soc_level_lower_limit-1, -1):
            vertex_list = [(trip_task.trip_id, column_2_time, soc_level), column_2_time_str, self.time_granularity]
            vertex = self.addVertex(vertex_list=vertex_list)
            # 添加第一列顶点和第二列顶点连接的边
            id_difference_col1_col2 = self.soc_level_number - trip_task.energy_consumption_level \
                                   - self.soc_level_lower_limit + 1
            vertex_col1_id = vertex.vertex_id - id_difference_col1_col2
            edge_list = ['task', self.vertex_set[vertex_col1_id], vertex]
            self.addEdge(edge_list=edge_list)


        # step 3: 循环添加后续的顶点，直到最后一列
        column_3_time = column_2_time + self.time_granularity * 60
        time_index = column_3_time
        col_index = 0
        # step 3.1 : 添加不满 SOC 阶段的顶点
        # step 3.2 : 添加满 SOC 阶段的顶点
        while time_index <= self.end_time:
        # while time_index < column_3_time + 5 * self.time_granularity * 60: # test
            if col_index < trip_task.energy_consumption_level: # 0 < 3
                for soc_level in range(self.soc_level_number - trip_task.energy_consumption_level + col_index + 1,
                                       self.soc_level_lower_limit - 1, -1):  # (8, 1- 1, -1) : 8-->1
                    time_index_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_index))
                    vertex_list = [(trip_task.trip_id, time_index, soc_level), time_index_str, self.time_granularity]
                    vertex = self.addVertex(vertex_list=vertex_list)
                    # 计算 vertex_charging_difference 和 vertex_waiting_difference
                    vertex_charging_difference = self.soc_level_number - trip_task.energy_consumption_level \
                                                 - self.soc_level_lower_limit + 1 + col_index
                    vertex_waiting_difference = self.soc_level_number - trip_task.energy_consumption_level \
                                                 - self.soc_level_lower_limit + 2 + col_index

                    if soc_level == self.soc_level_number - trip_task.energy_consumption_level + col_index + 1:
                        # 添加 charging 的边
                        vertex_previous_id = vertex.vertex_id - vertex_charging_difference
                        edge_list = ['charging', self.vertex_set[vertex_previous_id], vertex]
                        edge = self.addEdge(edge_list=edge_list)
                        edge.weight = self.battery_capacity / self.soc_level_number * \
                                      self.electricity_price(self.vertex_set[vertex_previous_id].start_time_str)
                    elif soc_level == self.soc_level_lower_limit:
                        # 添加 waiting 的边
                        vertex_previous_id = vertex.vertex_id - vertex_waiting_difference
                        edge_list = ['waiting', self.vertex_set[vertex_previous_id], vertex]
                        self.addEdge(edge_list=edge_list)
                    else:
                        # 添加 waiting 的边
                        vertex_previous_id = vertex.vertex_id - vertex_waiting_difference
                        edge_list = ['waiting', self.vertex_set[vertex_previous_id], vertex]
                        self.addEdge(edge_list=edge_list)
                        # 添加 charging 的边
                        vertex_previous_id = vertex.vertex_id - vertex_charging_difference
                        edge_list = ['charging', self.vertex_set[vertex_previous_id], vertex]
                        edge =self.addEdge(edge_list=edge_list)
                        edge.weight = self.battery_capacity / self.soc_level_number * \
                                      self.electricity_price(self.vertex_set[vertex_previous_id].start_time_str)
                col_index += 1
            else:
                # 过渡期结束
                for soc_level in range(self.soc_level_number, self.soc_level_lower_limit - 1, -1):  # (10, 1-1, -1) :10-->1
                    time_index_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_index))
                    vertex_list = [(trip_task.trip_id, time_index, soc_level), time_index_str, self.time_granularity]
                    vertex = self.addVertex(vertex_list=vertex_list)
                    # 计算 vertex_charging_difference 和 vertex_waiting_difference
                    vertex_charging_difference = self.soc_level_number - self.soc_level_lower_limit
                    vertex_waiting_difference = self.soc_level_number - self.soc_level_lower_limit + 1
                    if soc_level == self.soc_level_lower_limit:
                        # 添加 waiting 的边
                        vertex_previous_id = vertex.vertex_id - vertex_waiting_difference
                        edge_list = ['waiting', self.vertex_set[vertex_previous_id], vertex]
                        self.addEdge(edge_list=edge_list)
                    else:
                        # 添加 waiting 的边
                        vertex_previous_id = vertex.vertex_id - vertex_waiting_difference
                        edge_list = ['waiting', self.vertex_set[vertex_previous_id], vertex]
                        self.addEdge(edge_list=edge_list)
                        # 添加 charging 的边
                        vertex_previous_id = vertex.vertex_id - vertex_charging_difference
                        edge_list = ['charging', self.vertex_set[vertex_previous_id], vertex]
                        edge = self.addEdge(edge_list=edge_list)
                        edge.weight = self.battery_capacity / self.soc_level_number * \
                                      self.electricity_price(self.vertex_set[vertex_previous_id].start_time_str)
                        # print(edge.weight)
                col_index += 1
            time_index += self.time_granularity * 60
        self.plane_number += 1
        self.trip_in_vertex_list.append(trip_in_vertex_list)

        timer_3 = time.time()
        print('Plane added', self.plane_number)
        print('ratio', timer_a/(timer_3 - timer_2))
        print(len(self.coordinate_code_list))
        return 0

    def addPlaneDestination(self):
        # 目标平面只有一个顶点
        start_time = self.end_time
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        vertex_list = [(self.plane_number, start_time, self.soc_level_number), start_time_str, self.time_granularity]
        vertex = self.addVertex(vertex_list=vertex_list)

        for i in range(self.plane_number):
            if (i, start_time, self.soc_level_number) in self.coordinate_list:
                # 如果前面的平面内存在顶点的坐标为 (i, start_time, soc_level)，则建立这条边
                vertex_previous_id = self.coordinate_list.index((i, start_time, self.soc_level_number))
                edge_list = ['switch', self.vertex_set[vertex_previous_id], vertex]
                self.addEdge(edge_list=edge_list)
            else:
                print('addPlaneDestination error!')
        self.plane_number += 1
        return 0

    def electricity_price(self, charging_time_str, mode='TOU'):
        if mode == 'TOU':
            peak_price = 1.02756875
            flat_price = 0.67506875
            valley_price = 0.23106875

            # int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
            # time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_index))

            initial_time_str = charging_time_str[0:11] + '00:00:00'
            initial_time = int(time.mktime(time.strptime(initial_time_str, "%Y-%m-%d %H:%M:%S")))
            charging_time = int(time.mktime(time.strptime(charging_time_str, "%Y-%m-%d %H:%M:%S")))
            time_difference = charging_time - initial_time
            if time_difference >= 0 and time_difference < 25200: # 00:00 - 07:00
                price = valley_price
            elif time_difference >= 25200 and time_difference < 32400: # 07:00 - 09:00
                price = flat_price
            elif time_difference >= 32400 and time_difference < 41400:  # 09:00 - 11:30
                price = peak_price
            elif time_difference >= 41400 and time_difference < 50400: # 11:30 - 14:00
                price = flat_price
            elif time_difference >= 50400 and time_difference < 59400:  # 14:00 - 16:30
                price = peak_price
            elif time_difference >= 59400 and time_difference < 68400: # 16:30 - 19:00
                price = flat_price
            elif time_difference >= 68400 and time_difference < 75600:  # 19:00 - 21:00
                price = peak_price
            elif time_difference >= 75600 and time_difference < 82800: # 21:00 - 23:00
                price = flat_price
            else:
                price = valley_price
            return price
        else:
            return 'electricity price error!'

class Vertex(Graph.Vertex):
    def __init__(self, vertex_id, coordinate, start_time_str, duration):
        super(Vertex, self).__init__()
        self.vertex_id = vertex_id
        self.coordinate = coordinate    # The coordinate is: (trip, time, soc)
        self.coordinate_code = coordinate[1] * 10000000 + coordinate[0] * 1000 + coordinate[2]
        self.coordinate_str = [coordinate[0], start_time_str[-8:-3], coordinate[2]]
        self.start_time_str = start_time_str
        self.start_time = int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
        self.duration = duration

class Edge(Graph.Edge):
    def __init__(self, edge_id, attribute, end1, end2, directed=True, weight=0):
        super(Edge, self).__init__(vertex_end1=end1, vertex_end2=end2, directed=directed, weight=weight)
        self.edge_id = edge_id
        self.attribute = attribute # attribute: switch, task, charging, waiting

class Trip():
    def __init__(self, trip_id, attribute, start_time_str, duration, energy_consumption_level):
        self.trip_id = trip_id
        self.attribute = attribute # attribute: origin, task, destination
        self.start_time_str = start_time_str
        self.start_time = int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")))
        self.duration = duration # duration : minute
        # e_c_l is according to the soc_level_number defined in the graph
        self.energy_consumption_level = energy_consumption_level  # 3 is 30% of SOC






















