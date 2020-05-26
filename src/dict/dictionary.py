import marisa_trie
import codecs
import typing
import itertools
import src.dict.subclasses.graph as gr
import src.dict.subclasses.multisegmented as mlt
import src.dict.subclasses.exceptions as ex
import pickle


class Dictionary:
    """
    Dictionary object contains inflections

        Args:
            basic_files ([str]): array of names of the files in the format:
                            <infinitive>:<flexographic label>:<derivatives separated with colon>
                            where:
                                <flexographic label> is a sequence of capital letters,
                                                     optionally with an asterisk at the beginning
                                                     Codes:
                                                        *  - ambiguous word
                                                        AA - noun (pl. rzeczownik męski osobowowy)
                                                        AB - noun (pl. rzeczownik męski żywotny)
                                                        AC - noun (pl. rzeczownik męski nieżywotny)
                                                        AD - noun (pl. rzeczownik żeński itd)
                                                        AF - noun (pl. rzeczownik nijaki)
                                                        B  - verb
                                                        C  - adjective
                                                        F  - adverb

                                <derivatives separeted with colon> are word forms arranged in a fixed order
                                                                   depending on the part of speech that is
                                                                   defined by the first letter of the label.

        Attributes:
            multisegmented (mlt.multisegmented_module):
            lexical_relationships (dict):
            main_trie (marisa_trie.RecordTrie):
            reverse_trie (marisa_trie.Trie):
            translation_array ([int]):
            word_graph (gr.Graph):
    """

    def __init__(self, basic_files):
        try:
            self.multisegmented = mlt.multisegmented_module()
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

        self.word_graph = gr.Graph()
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

                    adjective = False
                    adjective_id = -1
                    if tmp[1].strip("*")[0] == "C":
                        adjective = True
                        adjective_id = child_id

                    for idx, word in enumerate(tmp[3:-1]):
                        if word != "##":
                            trie_main_id = self.main_trie.get(word)[0]
                            if trie_main_id not in shift_dict:
                                shift_dict[trie_main_id] = 0
                            child_id = self.main_trie[word][shift_dict[trie_main_id]][0]

                            if adjective and (idx + 1) % 7 == 0:
                                adjective_id = child_id

                            shift_dict[trie_main_id] += 1
                            self.word_graph.add_vertex(child_id, None)
                            self.word_graph.add_edge(lexem_id, child_id)

                            if adjective and (idx + 1) % 7 != 0:
                                self.word_graph.add_gender_edge(adjective_id, child_id)

                            self.translation_array[child_id] = self.reverse_trie[word]

    def get_parent(self, word: str) -> (str, str, typing.Sequence[str]):
        """
        Function that returns an infinitive of a word

            Args:
                word (str): derivative

            Returns:
                infinitive (str): Infinitive of word
                flexographic_labels (str): Sequence of capital letters, optionally with an asterisk at the beginning
                possible_matches ():
        """

        word_id = self.main_trie.get(word)[0][0]
        check_also = [x[0] for x in self.main_trie.get(word)[1:]]

        parent_id = self.word_graph.get_parent(word_id)
        if parent_id is None:
            return None, None, None

        parent_word_id = self.translation_array[parent_id]
        parents = {self.word_graph.get_parent(x) for x in check_also}
        possible_ids = {self.translation_array[x] for x in parents if x != parent_id}
        possible_matches = [self.reverse_trie.restore_key(x) for x in possible_ids]

        return self.reverse_trie.restore_key(parent_word_id), self.word_graph.get_label(parent_id), possible_matches

    def get_children(self, word: str) -> typing.List[str]:
        """
        Function that returns all known derivatives of a word

            Args:
                word (str): infinitive

            Returns:
                children_strings ([str]): Array of derivatives of a given word
        """

        word_id = self.main_trie.get(word)[0][0]
        children = self.word_graph.get_children(word_id)

        children_strings = []
        for child in children:
            child_word_id = self.translation_array[child]
            children_strings.append(self.reverse_trie.restore_key(child_word_id))

        return children_strings

    def add_multisegmented(self, files):
        """
        Function that adds multisegment to dictionary

            Args:
                files ([str]): Array of files names with multisegments
        """

        for file in files:
            with open(file, "r") as f:
                for line in f.readlines():
                    tokens = [x.strip() for x in line.split(";")[:-1]]

                    inter = None
                    if tokens[3] != "":
                        inter = [int(tokens[3][0]), int(tokens[3][1])]

                    stable_list = []
                    for char in tokens[1]:
                        if char == "*":
                            stable_list.append(False)
                        if char == "-":
                            stable_list.append(True)

                    segment = tokens[0].split(" ")
                    segment_lst = []
                    for seg in segment:
                        if "*" in seg:
                            continue

                        possible_ids = self.main_trie.get(seg, default=None)
                        if possible_ids is None:
                            raise ex.Key_Missing

                        for word_id in possible_ids:
                            if self.word_graph.has_gender(word_id[0]) and self.word_graph.get_gender_parent(
                                    word_id[0]) is not None:
                                continue
                            segment_lst.append(word_id[0])
                            break

                    key_tuple = tuple(segment_lst)
                    self.multisegmented.add_multisegmented(key_tuple, stable_list, inter)

    def get_parent_multisegmented(self, multi_word):
        """
        Function that returns infinitive of multisegment

            Args:
                multi_word ([str]): Array of words in multisegment
        """

        possible_ids_list = []
        for word in multi_word:
            possible_ids = self.main_trie.get(word, default=None)

            if possible_ids is None:
                raise ex.Key_Missing

            parents = {self.word_graph.get_gender_parent(x[0]) for x in possible_ids if self.word_graph.has_gender(x)}
            parents.update(
                {self.word_graph.get_parent(x[0]) for x in possible_ids if not self.word_graph.has_gender(x)})
            possible_ids_list.append(parents)

        all_combinations = itertools.product(*possible_ids_list)
        for combination in all_combinations:
            if self.multisegmented.is_multisegmented(combination):
                translated_ids = [self.translation_array[x] for x in combination]
                return "".join([self.reverse_trie.restore_key(x) for x in
                                translated_ids]), self.multisegmented.get_multitsegmented_info(combination)

    def get_all_relationships(self):
        """
        Function that returns all relationships name present in dictionary

            Returns:
                relationship_names (list(str)): List of relationships names
        """
        return list(self.lexical_relationships.keys());

    def __add_new_relationship__(self, relationship_name):
        """
        Function that adds relationship name to dictionary

            Args:
                relationship_name (str): Name of relationship

            Raises:
                Relationship_exists

            Returns:
                None
        """
        rel_name = relationship_name.lower()
        if rel_name in self.lexical_relationships.keys():
            raise ex.Relationship_exists("Relationship {} already exists and as such cannot be added",
                                         relationship_name)
        if len(self.lexical_relationships.keys()):
            max_ind = max(self.lexical_relationships.values())
        else:
            max_ind = 0
        self.lexical_relationships[relationship_name] = max_ind + 1

    def add_gradation_relationship(self, file):
        """
        Function that adds gradation relationship

            Args:
                file (str): name of the file in the format:
                            equal:higher:highest

            Raises:
                Key_Missing: Missing word grade - graduation of a single word from a given file is incomplete

            Returns:
                None
        """

        # hr - stands for 2 degree of gradation
        # hst - stands for 3 degree of gradation
        if "hr" not in self.lexical_relationships.keys():
            self.__add_new_relationship__("hr")
            self.__add_new_relationship__("hst")

        with codecs.open(file, "r", encoding="utf8") as f:
            for line in f.readlines():
                words = [word.strip() for word in line.split(":")[:-1]]

                eq_degree = self.main_trie.get(words[0])[0]
                if eq_degree is None:
                    raise ex.Key_Missing

                hr_degree = self.main_trie.get(words[1])[0]
                if hr_degree is None:
                    raise ex.Key_Missing

                hst_degree = self.main_trie.get(words[2])[0]
                if hst_degree is None:
                    raise ex.Key_Missing

                self.word_graph.add_relationship_edge(eq_degree[0], hr_degree[0], self.lexical_relationships["hr"])
                self.word_graph.add_relationship_edge(eq_degree[0], hst_degree[0], self.lexical_relationships["hst"])

    def add_im_norm_relationship(self, file):
        """
        Function that adds gradation relationship

            Args:
                file (str): name of the file in the format:
                            lexem:label:im1:im2:im3:im4:noun

            Returns:
                None
        """

        # relationship_name - imieslow for first 4, rzeczownik for the last
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
        Function that adds gradation relationship

            Args:
                file (str): name of the file in the format:
                            lexem:label:rel_word1:rel_word2:...

                relationship_name (str): Name of relationship

            Returns:
                None
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
                        self.word_graph.add_relationship_edge(root_id, other_id,
                                                              self.lexical_relationships[relationship_name])

    def get_word_by_relationship(self, relationship_name, word):
        """
        Function that returns base form of given word

            Args:
                relationship_name (str): Name of relationship
                word (str):

            Raises:
                Relationship_not_found: Notifies that given relationship is not present in dictionary

            Returns:
                base_form (str): Base form of word
                flexographic_labels (str): Sequence of capital letters, optionally with an asterisk at the beginning
                possible_matches ():
        """

        try:
            rel_index = self.lexical_relationships[relationship_name]
        except:
            raise ex.Relationship_not_found("Relationship by which you are trying to search does not exist yet")

        word_id = self.main_trie.get(word)[0][0]
        check_also = [x[0] for x in self.main_trie.get(word)[1:]]

        parent_id = self.word_graph.get_parent(word_id)
        if parent_id is None:
            parent_id = word_id

        parents = {self.word_graph.get_parent(x) for x in check_also}
        rel_id = self.word_graph.get_word_by_relationship(parent_id, rel_index)[0]
        if rel_id is None:
            for x in parents:
                rel_id = self.word_graph.get_word_by_relationship(x, rel_index)[0]
                if x is not None:
                    break
            if rel_id is None:
                return None, None, None

        possible_rel_ids = {self.word_graph.get_word_by_relationship(x, rel_index) for x in parents}
        possible_ids = {self.translation_array[x] for x in possible_rel_ids if x != rel_id}
        possible_matches = [self.reverse_trie.restore_key(x) for x in possible_ids]

        return self.reverse_trie.restore_key(self.translation_array[rel_id]), \
               self.word_graph.get_label(rel_id), possible_matches

    @staticmethod
    def export_dict(dictionary, file: str):
        """
        Function that returns imported Dictionary object from file

            Args:
                dictionary (Dictionary): Dictionary object to export
                file (str): Name of file to import from

            Returns:
                None
        """

        pickle.dump(dictionary, open(file, "wb"))

    @staticmethod
    def import_dict(file: str):
        """
        Function that returns imported Dictionary object from file

            Args:
                file (str): Name of file to import from

            Returns:
                dictionary (Dictionary): Imported dictionary object from file
        """
        return pickle.load(open(file, "rb"))
