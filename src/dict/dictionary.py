import marisa_trie
import codecs
import typing
import src.dict.graph.graph as gr

class Dictionary():
    def __init__(self, file):
        with codecs.open(file, "r", encoding="utf8") as f:
            keys = [x.strip() for y in f.readlines() for x in y.split(":")[2:-1] if x.strip() != "##"]
            values = [(i,) for i in range(len(keys))]
            fmt = "<H"

            self.main_trie = marisa_trie.RecordTrie(fmt, zip(keys, values))
            self.reverse_trie = marisa_trie.Trie(keys)
            self.translation_array = [-1 for i in range(len(keys))]

        self.word_graph = gr.graph()

        with codecs.open(file, "r", encoding="utf8") as f:
            for line in f.readlines():
                tmp = [x.strip() for x in line.split(":")]
                id_dict = {x: 0 for x in tmp}
                lexem_id = self.main_trie[tmp[2]][id_dict[tmp[2]]][0]
                id_dict[tmp[2]] += 1
                self.word_graph.add_vertex(lexem_id, tmp[1])
                self.translation_array[lexem_id] = self.reverse_trie[tmp[2]]

                for word in tmp[3:-1]:
                    if word != "##":
                        child_id = self.main_trie[word][id_dict[word]][0]
                        id_dict[word] += 1
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


