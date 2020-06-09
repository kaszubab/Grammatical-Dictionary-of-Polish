import unittest

from src.dict import dictionary


class DictionaryTests(unittest.TestCase):
    def test_export_import(self):
        test_dict = dictionary.Dictionary(["test_data/test_file.txt"])
        dictionary.Dictionary.export_dict(test_dict, "test_data/test_file.pickle")
        imported_dict = dictionary.Dictionary.import_dict("test_data/test_file.pickle")
        self.assertEqual(test_dict, imported_dict)

    def test_get_parent(self):
        test_dict = dictionary.Dictionary(["test_data/test_file.txt"])
        self.assertEqual(test_dict.get_parent("Gdańska")[0], "Gdańsk")
        self.assertEqual(test_dict.get_parent("Gdańska")[1], "AA")

    def test_get_children(self):
        test_dict = dictionary.Dictionary(["test_data/test_file.txt"])
        print(test_dict.get_children("Gdańsk"))
        self.assertEqual(test_dict.get_children("Gdańsk"), ['Gdański', 'Gdańska', 'Gdańsków', 'Gdańskowi', 'Gdańskom',
                         'Gdańsk', 'Gdański', 'Gdańskiem', 'Gdańskami', 'Gdańsku', 'Gdańskach', 'Gdańsku', 'Gdański'])


if __name__ == '__main__':
    unittest.main()
