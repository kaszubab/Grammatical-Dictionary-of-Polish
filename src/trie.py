import marisa_trie
import codecs
import graph.graph as gr



def build_trie(file):
    with codecs.open(file, "r", encoding="utf8") as f:
        keys = [x.strip() for y in f.readlines() for x in y.split(":")[2:-1] if x.strip() != "##"]
        values = [(i,) for i in range(len(keys))]
        fmt = "<H"

        main_trie = marisa_trie.RecordTrie(fmt, zip(keys, values))
        word_trie = marisa_trie.Trie(keys)
        translation_array = [-1 for i in range(len(keys))]

    children_graph = gr.graph()

    with codecs.open(file, "r", encoding="utf8") as f:
        for line in f.readlines():
            tmp = [x.strip() for x in  line.split(":")]
            id_dict = {x: 0 for x in tmp}
            lexem_id = main_trie[tmp[2]][id_dict[tmp[2]]][0]
            id_dict[tmp[2]]+=1
            children_graph.add_vertex(lexem_id, tmp[1])
            translation_array[lexem_id] = word_trie[tmp[2]]

            for word in tmp[3:-1]:
                if word != "##":
                    child_id = main_trie[word][id_dict[word]][0]
                    id_dict[word] += 1
                    children_graph.add_vertex(child_id, None)
                    children_graph.add_edge(lexem_id, child_id)
                    translation_array[child_id] = word_trie[word]

    return main_trie, children_graph, translation_array, word_trie

def get_children(word, m_trie, trie, translation_array, graph):
    word_id = m_trie.get(word)[0][0]
    check_also = [x[0] for x in m_trie.get(word)[1:]]

    children = graph.get_children(word_id)
    children_strings = []
    for child in children:
        child_word_id = translation_array[child]
        children_strings.append(trie.restore_key(child_word_id))

    return children_strings


if __name__ == '__main__':
    trie, graph, trans_array, list_trie = build_trie("pospolite.txt")
    children = get_children("pies", trie, list_trie, trans_array, graph)
    print(children)
