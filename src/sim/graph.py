import networkx as nx

class Graph:
    """A directed acyclic graph that can be used for tracking
    object state transitions. Edged from one object to another
    can have attributes attached to them (such as weight) and
    such attributes can be used to get the optimum path."""

    def __init__(self, nodes, edges):
        self.g = nx.Graph()
        self.g.add_nodes_from(nodes)
        self.g.add_edges_from(edges)

    def __str__(self):
        print(g.__str__())

    def add_node(self, node, attributes):
        self.g.add_node(node, attr_dic=attributes)

    def add_edge(self, fromNode, toNode, attributes):
        self.g.add_edge(fromNode, toNode)
        self.g.edges[fromNode, toNode].update(attributes)

    """Returns the lowest cost path by the defined attribute. See the
       test test_graph_shortest_path for an example usage."""
    def lowest_cost_path_by(self, attribute, fromNode, toNode):
        nodes = nx.dijkstra_path(self.g, fromNode, toNode, attribute)
        return nodes
