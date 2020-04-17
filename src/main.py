import src.dict.dictionary as dict

if __name__ == '__main__':
    dictionary = dict.Dictionary("pospolite.txt")
    print(dictionary.get_children("pies"))
    print(dictionary.get_parent("psa"))
