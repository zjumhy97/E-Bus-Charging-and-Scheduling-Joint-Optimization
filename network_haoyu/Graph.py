class Graph():
    def __init__(self):
        self.vertex_set = []
        self.edge_set = []
        self.vertex_size = 0
        self.edge_size = 0
        self.graph_attribute = None

    def graphSize(self):
        self.vertex_size = len(self.vertex_set)
        self.edge_size = len(self.edge_set)
        return self.vertex_size, self.edge_size

class Vertex():
    def __init__(self):
        self.edge_id_out = []
        self.edge_id_in = []


class Edge():
    def __init__(self, vertex_end1, vertex_end2, directed=True, weight=1):
        self.end1 = vertex_end1
        self.end2 = vertex_end2
        self.directed = directed
        self.weight = weight
        self.vertex_id_pair = [vertex_end1.vertex_id, vertex_end2.vertex_id]
        if self.directed:
            self.start = vertex_end1
            self.end = vertex_end2

