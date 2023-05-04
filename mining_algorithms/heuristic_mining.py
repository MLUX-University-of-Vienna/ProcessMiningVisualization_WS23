from graphviz import Digraph
import numpy as np

class HeuristicMining():
    def __init__(self, log):
        self.log = log
        self.events, self.appearence_frequency = self.__filter_out_all_events()
        self.succession_matrix = self.__create_succession_matrix()
        self.dependency_matrix = self.__create_dependency_matrix()

        # Graph modifiers
        self.edge_thickness_amplifier = 1
        self.max_edge_thickness = 5
    
    def create_dependency_graph_with_graphviz(self, dependency_treshhold, min_frequency):
        dependency_graph = self.__create_dependency_graph(dependency_treshhold, min_frequency)
        
        # create graph
        graph = Digraph()

        # add nodes to graph
        for node in self.events:
            node_freq = self.appearence_frequency.get(node)
            w = 1 + node_freq/self.get_max_frequency()
            h = w/2
            graph.node(str(node), label = str(node)+"\n"+str(node_freq),width = str(w), height = str(h))

        # add edges to graph
        for i in range(len(self.events)):
            for j in range(len(self.events)):
                if dependency_graph[i][j] == 1.:
                    if dependency_treshhold == 0:
                        edge_thickness = 0.1
                    else:
                        edge_thickness = self.dependency_matrix[i][j]/dependency_treshhold * self.edge_thickness_amplifier
                        if(edge_thickness>self.max_edge_thickness):
                            edge_thickness = self.max_edge_thickness
                    graph.edge(str(self.events[i]), str(self.events[j]), penwidth = str(edge_thickness), label = str(int(self.succession_matrix[i][j])))

        #add start node
        graph.node("start", shape='doublecircle', style='filled',fillcolor='green')
        for node in self.__get_start_nodes():
            graph.edge("start", str(node), penwidth = str(0.1) )

        #add end node
        graph.node("end", shape='doublecircle', style='filled',fillcolor='red')
        for node in self.__get_end_nodes():
            graph.edge(str(node), "end", penwidth =str( 0.1) )  

        return graph
    
    def get_max_frequency(self):
        max_freq = 0
        for value in list(self.appearence_frequency.values()):
            if value > max_freq:
                max_freq= value
        return max_freq
    
    def __filter_out_all_events(self):
        dic = {}
        for trace in self.log:
            for activity in trace:
                if activity in dic:
                    dic[activity] = dic[activity]+1
                else:
                    dic[activity] = 1

        activities = list(dic.keys())
        return activities, dic

    def __create_succession_matrix(self):
        succession_matrix = np.zeros((len(self.events),len(self.events)))
        for trace in self.log:
            index_x = -1
            for element in trace:
                
                if index_x <0:
                    index_x +=1
                    continue
                x = self.events.index(trace[index_x])
                y = self.events.index(element)
                succession_matrix[x][y]+=1
                index_x +=1
        return succession_matrix
    
    def __get_start_nodes(self):
        #a start node is a node where an entire column in the succession_matrix is 0.
        start_nodes = []
        for case in self.log:
            if case[0] not in start_nodes:
                start_nodes.append(case[0])
        
        return start_nodes
        
    
    def __get_end_nodes(self):
        #an end node is a node where an entire row in the succession_matrix is 0.
        end_nodes = []
        for case in self.log:
            last_index = len(case)-1
            if case[last_index] not in end_nodes:
                end_nodes.append(case[last_index])
        
        return end_nodes

    def __create_dependency_matrix(self):
        dependency_matrix = np.zeros(self.succession_matrix.shape)
        y = 0
        for row in self.succession_matrix:
            x = 0
            for i in row:
                if x == y:
                    dependency_matrix[x][y] = self.succession_matrix[x][y]/(self.succession_matrix[x][y]+1)
                else:
                    dependency_matrix[x][y] = (self.succession_matrix[x][y]-self.succession_matrix[y][x])/(self.succession_matrix[x][y]+self.succession_matrix[y][x]+1)
                x+=1
            y+=1
        return dependency_matrix

    def __create_dependency_graph(self, dependency_treshhold, min_frequency):
        dependency_graph = np.zeros(self.dependency_matrix.shape)
        y = 0
        for row in dependency_graph:
            for x in range(len(row)):
                if self.dependency_matrix[y][x] >= dependency_treshhold and self.succession_matrix[y][x] >= min_frequency:
                    dependency_graph[y][x]+= 1          
            y+=1

        return dependency_graph