import src.dict as dict

if __name__ == '__main__':

    dictionary = dict.Dictionary(["pospolite.txt"])
    print(dictionary.get_children("pies"))
    print(dictionary.get_children("albo"))
    print(dictionary.get_children("biały"))


    print(dictionary.get_parent("psa"))
    dictionary.add_gradation_relationship("adj.txt")
    print(dictionary.get_all_relationships())
    print(dictionary.get_parent("największy"))
    print(dictionary.get_word_by_relationship("hst", "największy"))
    dictionary.add_multisegmented(["WS_test.txt"])

    print(dictionary.get_parent_multisegmented("złej Apokalipsy"))
    print(dictionary.get_parent_multisegmented("białego Argusa"))
    print(dictionary.get_parent_multisegmented("bielą złą"))
    print(dictionary.get_parent_multisegmented("albo Argusowi"))

    print(dictionary.get_children_multisegmented("albo Argus"))






