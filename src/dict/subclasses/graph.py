import src.dict.subclasses.exceptions as ex

class graph:
    class graph_node:
        def __init__(self, label):
            self.label = label
            self.parent = None
            self.children = None
            self.gender_parent = None # used only with adjectives
            self.gender_children = None # used only with adjectives
            self.has_genders = False
            self.relationships = {}

        def add_child(self, children):
            if self.children is None:
                self.children = []
            self.children.append(children)

        def add_gender_child(self, children):
            if self.gender_children is None:
                self.gender_children = []
            self.gender_children.append(children)
    def __init__(self):
        self.nodes = {}

    def add_vertex(self, vert_id, label):
        self.nodes[vert_id] = self.graph_node(label)

    def add_edge(self, from_v, to_v):
        self.nodes[from_v].add_child(to_v)
        self.nodes[to_v].parent = from_v

    def add_gender_edge(self, from_v, to_v):
        self.nodes[from_v].has_genders = True
        self.nodes[to_v].has_genders = True

        self.nodes[from_v].add_child(to_v)
        self.nodes[to_v].gender_parent = from_v

    def add_relationship_edge(self, from_v, to_v, relationship_id):
        if relationship_id not in self.nodes[from_v].relationships.keys():
            self.nodes[from_v].relationships[relationship_id]= []

        if relationship_id not in self.nodes[from_v].relationships.keys():
            self.nodes[to_v].relationships[relationship_id]= []

        self.nodes[from_v].relationships[relationship_id].append(to_v)
        self.nodes[to_v].relationships[relationship_id].append(from_v)

    def get_children(self, id):
        return self.nodes[id].children

    def get_parent(self, id):
        return self.nodes[id].parent

    def has_gender(self,id):
        return self.nodes[id].has_genders

    def get_gender_parent(self, id):
        return self.nodes[id].gender_parent

    def get_gender_children(self, id):
        return self.nodes[id].gender_children

    def get_label(self, id):
        return self.nodes[id].label

    def get_word_by_relationship(self, id, relationship_id):
        self.nodes[id].relationships.get(relationship_id, default=None)
