import marisa_trie
import codecs
import typing
import src.dict.subclasses.graph as gr
import src.dict.subclasses.exceptions as ex

class Dictionary():
    def __init__(self, basic_files, multi_segment_files):
        try:
            keys = []
            values = []
            last_ind = 0
            for file in basic_files:
                with codecs.open(file, "r", encoding="utf8") as f:
                    new_keys = [x.strip() for y in f.readlines() for x in y.split(":")[2:-1] if x.strip() != "##"]
                    keys += new_keys
                    values += [(i + last_ind,) for i in range(len(new_keys))]
                    last_ind += len(new_keys)

            fmt = "<H"
            self.lexical_relationships = {}
            self.main_trie = marisa_trie.RecordTrie(fmt, zip(keys, values))
            self.reverse_trie = marisa_trie.Trie(keys)
            self.translation_array = [-1 for i in range(len(keys))]
        except FileNotFoundError:
            print("File not found")
            raise

        self.word_graph = gr.graph()
        shift_dict = {}
        for file in basic_files:
            with codecs.open(file, "r", encoding="utf8") as f:
                for line in f.readlines():
                    tmp = [x.strip() for x in line.split(":")]
                    trie_main_id = self.main_trie.get(tmp[2])[0]

                    if trie_main_id not in shift_dict:
                        shift_dict[trie_main_id] = 0

                    lexem_id = self.main_trie[tmp[2]][shift_dict[trie_main_id]][0]
                    shift_dict[trie_main_id] += 1
                    self.word_graph.add_vertex(lexem_id, tmp[1])
                    self.translation_array[lexem_id] = self.reverse_trie[tmp[2]]

                    for word in tmp[3:-1]:
                        if word != "##":
                            trie_main_id = self.main_trie.get(word)[0]
                            if trie_main_id not in shift_dict:
                                shift_dict[trie_main_id] = 0
                            child_id = self.main_trie[word][shift_dict[trie_main_id]][0]
                            shift_dict[trie_main_id] += 1
                            self.word_graph.add_vertex(child_id, None)
                            self.word_graph.add_edge(lexem_id, child_id)
                            self.translation_array[child_id] = self.reverse_trie[word]

    def get_children(self, word: str) -> typing.List[str]:

        word_id = self.main_trie.get(word)[0][0]
        check_also = [x[0] for x in self.main_trie.get(word)[1:]]
        children = self.word_graph.get_children(word_id)
        children_strings = []
        for child in children:
            child_word_id = self.translation_array[child]
            children_strings.append(self.reverse_trie.restore_key(child_word_id))
        return children_strings

    def get_parent(self, word: str) -> (str, str, typing.Sequence[str]):
        word_id = self.main_trie.get(word)[0][0]
        check_also = [x[0] for x in self.main_trie.get(word)[1:]]

        parent_id = self.word_graph.get_parent(word_id)
        parent_word_id = self.translation_array[parent_id]

        parents = {self.word_graph.get_parent(x) for x in check_also}
        possible_ids = {self.translation_array[x] for x in parents if x != parent_id}
        possible_matches = [self.reverse_trie.restore_key(x) for x in possible_ids]
        return self.reverse_trie.restore_key(parent_word_id), self.word_graph.get_label(parent_id),possible_matches

    def get_all_relationships(self):
        return self.lexical_relationships.keys();

    def __add_new_relationship__(self, relationship_name):
        rel_name = relationship_name.lower()
        if rel_name in self.lexical_relationships.keys():
            raise ex.Relationship_exists("Relationship {} already exists and as such cannot be added", relationship_name)
        max_ind = max(self.lexical_relationships.values())
        self.lexical_relationships[relationship_name] = max_ind+1

    def add_gradation_relationship(self, file):
        """
        adds gradation relationship
        filename - name of the file in the format - equal:higher:highest
        hr - stands for 2 degree of gradation
        hst - stands for 3 degree of gradation
        """

        if "hr" not in self.lexical_relationships.keys():
            self.__add_new_relationship__("hr")
            self.__add_new_relationship__("hst")

        with codecs.open(file, "r", encoding="utf8") as f:
            for line in f.readlines():
                words = [word.strip() for word in line.split(":")[:-1]]
                eq_degree = self.main_trie.get(words[0])[0]
                hr_degree = self.main_trie.get(words[1])[0]
                hst_degree = self.main_trie.get(words[2])[0]
                self.word_graph.add_relationship_edge(eq_degree, hr_degree, self.lexical_relationships["hr"])
                self.word_graph.add_relationship_edge(eq_degree, hst_degree, self.lexical_relationships["hst"])




    def add_im_norm_relationship(self, file):
        """
        adds gradation relationship
        filename - name of the file in the format - lexem:label:im1:im2:im3:im4:noun
        relationship_name = imieslow for first 4, rzeczownik for the last
        """

        rel_name = "imieslow"
        rel2_name = "rzeczownik"
        if rel_name not in self.lexical_relationships.keys():
            self.__add_new_relationship__(rel_name)

        if rel2_name not in self.lexical_relationships.keys():
            self.__add_new_relationship__(rel2_name)

        with codecs.open(file, "r", encoding="utf8") as f:
            for line in f.readlines():
                words = [word.strip() for word in line.split(":")[:-1]]
                root_id = self.main_trie.get(words[0])[0]
                for word in words[2:-1]:
                    if word != "#":
                        other_id = self.main_trie.get(word)[0]
                        self.word_graph.add_relationship_edge(root_id, other_id, self.lexical_relationships[rel_name])
                noun_id = self.main_trie.get(words[-1])[0]
                self.word_graph.add_relationship_edge(root_id, noun_id, self.lexical_relationships[rel2_name])




    def add_generic_relationship(self, file, relationship_name):
        """
        adds gradation relationship
        filename_structure - name of the file in the format - lexem:label:rel_word1:rel_word2:...
        relationship_name = relationship_name
        """
        if relationship_name not in self.lexical_relationships.keys():
            self.__add_new_relationship__(relationship_name)

        with codecs.open(file, "r", encoding="utf8") as f:
            for line in f.readlines():
                words = [word.strip() for word in line.split(":")[:-1]]
                root_id = self.main_trie.get(words[0])[0]
                for word in words[2:]:
                    if word != "#":
                        other_id = self.main_trie.get(word)[0]
                        self.word_graph.add_relationship_edge(root_id, other_id, self.lexical_relationships[relationship_name])

    def get_word_by_relationship(self, relationship_name, word):
        try:
            rel_index = self.lexical_relationships[relationship_name]
        except:
            raise ex.Relationship_not_found("Relationship by which you are trying to search does not exist yet")

        word_id = self.main_trie.get(word)[0][0]
        check_also = [x[0] for x in self.main_trie.get(word)[1:]]
        parent_id = self.word_graph.get_parent(word_id)
        parents = {self.word_graph.get_parent(x) for x in check_also}

        rel_id = self.word_graph.get_word_by_relationship(parent_id, rel_index)
        possible_rel_ids = {self.word_graph.get_word_by_relationship(x, rel_index) for x in parents}

        possible_ids = {self.translation_array[x] for x in possible_rel_ids if x != rel_id}
        possible_matches = [self.reverse_trie.restore_key(x) for x in possible_ids]
        return self.reverse_trie.restore_key(self.translation_array[rel_id]), self.word_graph.get_label(rel_id), possible_matches

