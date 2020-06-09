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
            last_index = 0
            for file in basic_files:
                with codecs.open(file, "r", encoding="utf8") as openned_file:
                    new_keys = []
                    for line in openned_file:
                        line_split = line.split(":")
                        if line_split[1].strip("* ")[0] in ["C", "D"]:
                            line_split = [line_split[0]] + line_split[3:9] + line_split[16:-3]
                        else:
                            line_split = [line_split[0]] + line_split[3:-1]
                        new_keys += [token.strip() for token in line_split
                                     if token.strip() != "##" and token.strip() != "#"]

                    keys += new_keys
                    values += [(current_index + last_index,) for current_index in range(len(new_keys))]
                    last_index += len(new_keys)

            content_format = "<H"
            self.lexical_relationships = {}
            self.main_trie = marisa_trie.RecordTrie(content_format, zip(keys, values))
            self.reverse_trie = marisa_trie.Trie(keys)
            self.translation_array = [-1 for i in range(len(keys))]
        except FileNotFoundError:
            print("File not found")
            raise

        self.word_graph = gr.Graph()
        shift_dict = {}
        cases = [case for case in gr.Cases]
        genders = [gender for gender in gr.Genders]

        for file in basic_files:
            with codecs.open(file, "r", encoding="utf8") as openned_file:
                for line in openned_file.readlines():
                    line_split = line.split(":")
                    if line_split[1].strip("* ")[0] in ["C", "D"]:
                        line_split = line_split[0:2] + line_split[3:9] + line_split[16:-3]
                    else:
                        line_split = line_split[0:2] + line_split[3:-1]
                    print(line_split)
                    tmp = [x.strip() for x in line_split]

                    trie_main_id = self.main_trie.get(tmp[0])[0][0]

                    if trie_main_id not in shift_dict:
                        shift_dict[trie_main_id] = 0

                    lexem_id = self.main_trie[tmp[0]][shift_dict[trie_main_id]][0]
                    shift_dict[trie_main_id] += 1

                    word_type = tmp[1].strip("*")[0]
                    gender_parent_id = None

                    if word_type in ["A", "C", "D"]:
                        self.word_graph.add_gender_vertex(lexem_id, tmp[1],cases[0] ,genders[0])
                        gender_parent_id = lexem_id
                    else:
                        self.word_graph.add_vertex(lexem_id, tmp[1])

                    self.translation_array[lexem_id] = self.reverse_trie[tmp[0]]

                    for idx, word in enumerate(tmp[2:]):
                        if word != "##" and word != "#":
                            trie_main_id = self.main_trie.get(word)[0][0]
                            if trie_main_id not in shift_dict:
                                shift_dict[trie_main_id] = 0

                            child_id = self.main_trie.get(word)[shift_dict[trie_main_id]][0]
                            shift_dict[trie_main_id] += 1

                            if word_type in ["A", "C", "D"]:
                                if word_type in ["C", "D"] and idx + 1 > 34:
                                    continue

                                self.word_graph.add_gender_vertex(child_id, None, cases[(idx+1) % 7],genders[(idx+1)//7])
                                if (idx + 1) % 7 ==0:
                                    gender_parent_id = child_id
                                else:
                                    self.word_graph.add_gender_edge(gender_parent_id, child_id)
                            else:
                                self.word_graph.add_vertex(child_id, None)

                            self.word_graph.add_edge(lexem_id, child_id)
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
            with open(file, "r", encoding="utf8") as f:
                for line in f.readlines():
                    tokens = [x.strip() for x in line.split(";")[:-1]]

                    interchangeable = None
                    if tokens[3] != "":
                        interchangeable = [int(tokens[3][0]), int(tokens[3][1])]

                    stable_list = []
                    for char in tokens[1]:
                        if char == "*":
                            stable_list.append(False)
                        if char == "-":
                            stable_list.append(True)

                    segment = tokens[0].strip("# ").split(" ")
                    segment_lst = []
                    index = 0
                    for word in segment:
                        if "*" in word:
                            continue

                        possible_ids = self.main_trie.get(word, default=None)
                        if possible_ids is None:
                            raise ex.Key_Missing

                        for word_id in possible_ids:
                            if not stable_list[index] and  (not self.word_graph.has_gender(word_id[0]) or self.word_graph.get_gender_parent(
                                    word_id[0]) is not None):
                                continue
                            segment_lst.append(word_id[0])
                            break
                        if (segment_lst[-1],) not in possible_ids:
                            raise ex.Key_Missing

                    key_tuple = tuple(segment_lst)
                    self.multisegmented.add_multisegmented(key_tuple, stable_list, interchangeable)

    def get_parent_multisegmented(self, multi_word):
        """
        Function that returns infinitive of multisegment

            Args:
                multi_word ([str]): Array of words in multisegment
        """

        possible_ids_list = []
        for word in multi_word.split():
            possible_ids = self.main_trie.get(word, default=None)

            print(word)
            print(possible_ids)
            # print(self.word_graph.get_parent(143))
            if possible_ids is None:
                raise ex.Key_Missing

            parents = {self.word_graph.get_gender_parent(word_id[0]) for word_id
                       in possible_ids if self.word_graph.has_gender(word_id[0])}
            parents.update({self.word_graph.get_parent(word_id[0]) for word_id
                            in possible_ids if not self.word_graph.has_gender(word_id[0])})
            possible_ids_list.append(parents)

        all_combinations = itertools.product(*possible_ids_list)
        for combination in all_combinations:
            if self.multisegmented.is_multisegmented(combination):
                translated_ids = [self.translation_array[x] for x in combination]
                return " ".join([self.reverse_trie.restore_key(x) for x in
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

                print(eq_degree[0], hr_degree[0])

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
