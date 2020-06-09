import src.dict.subclasses.exceptions as ex
from enum import Enum

class Genders(Enum):
    MASCULINE = 1
    FEMININE = 2
    NEUTER = 3
    MASCULINE_PERSONAL = 4
    MASCULINE_NON_PERSONAL = 5

class Cases(Enum):
    NOMINATIVE = 1
    INSTRUMENTAL = 2
    ACCUSATIVE = 3
    GENITIVE = 4
    LOCATIVE = 5
    DATIVE = 6
    VOCATIVE = 7


class Graph:
    class graph_node:
        def __init__(self, label):
            self.label = label
            self.parent = None
            self.children = None
            self.relationships = {}

        def add_child(self, children):
            if self.children is None:
                self.children = []
            self.children.append(children)

    class gender_node(graph_node):
        def __init__(self, label, case, gender):
            self.case = case
            self.gender = gender
            self.gender_children = None
            self.gender_parent = None
            super().__init__(label)

        def add_gender_child(self, children):
            if self.gender_children is None:
                self.gender_children = []
            self.gender_children.append(children)

    def __init__(self):
        self.nodes = {}

    def add_vertex(self, vertex_index, label):
        self.nodes[vertex_index] = self.graph_node(label)

    def add_gender_vertex(self, vertex_index, label, case, gender):
        self.nodes[vertex_index] = self.gender_node(label, case, gender)

    def add_edge(self, from_v, to_v):
        self.nodes[from_v].add_child(to_v)
        self.nodes[to_v].parent = from_v

    def add_gender_edge(self, from_v, to_v):
        self.nodes[from_v].add_gender_child(to_v)
        self.nodes[to_v].gender_parent = from_v

    def add_relationship_edge(self, from_v, to_v, relationship_id):
        if relationship_id not in self.nodes[from_v].relationships.keys():
            self.nodes[from_v].relationships[relationship_id]= []

        if relationship_id not in self.nodes[to_v].relationships.keys():
            self.nodes[to_v].relationships[relationship_id]= []

        self.nodes[from_v].relationships[relationship_id].append(to_v)
        self.nodes[to_v].relationships[relationship_id].append(from_v)

    def get_children(self, id):
        return self.nodes[id].children

    def get_parent(self, id):
        return self.nodes[id].parent

    def get_gender_parent(self, id):
        return self.nodes[id].gender_parent

    def get_gender_children(self, id):
        return self.nodes[id].gender_children

    def has_gender(self, id):
        return isinstance(self.nodes[id], self.gender_node)

    def get_label(self, id):
        return self.nodes[id].label

    def get_word_by_relationship(self, id, relationship_id):
        return self.nodes[id].relationships.get(relationship_id)
