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
        self.assertEqual(test_dict.get_parent("Gdański")[0], "Gdańsk")
        self.assertEqual(test_dict.get_parent("Gdański")[1], "AA")

    def test_get_children(self):
        test_dict = dictionary.Dictionary(["test_data/test_file.txt"])
        self.assertEqual(test_dict.get_children("Gdańsk"), ['Gdański', 'Gdańska', 'Gdańsków',
                                                            'Gdańskowi', 'Gdańskom', 'Gdańsk',
                                                            'Gdański', 'Gdańskiem', 'Gdańskami',
                                                            'Gdańsku', 'Gdańskach', 'Gdańsku', 'Gdański'])

    def test_get_all_relationships(self):
        test_dict = dictionary.Dictionary(["test_data/pospolite.txt"])
        test_dict.add_gradation_relationship("test_data/adj.txt")
        self.assertEqual(test_dict.get_all_relationships(), ['hr', 'hst'])

    def test_get_word_by_relationship(self):
        test_dict = dictionary.Dictionary(["test_data/pospolite.txt"])
        test_dict.add_gradation_relationship("test_data/adj.txt")
        self.assertEqual(test_dict.get_word_by_relationship("hst", "największy"), ('duży', '*CAB', []))

    def test_get_parent_multisegmented(self):
        test_dict = dictionary.Dictionary(["test_data/pospolite.txt"])
        test_dict.add_multisegmented(["test_data/WS_test.txt"])
        self.assertEqual(test_dict.get_parent_multisegmented("złej Apokalipsy"),
                         ('zła Apokalipsa', [[False, False], None]))

    def test_get_children_multisegmented(self):
        test_dict = dictionary.Dictionary(["test_data/pospolite.txt"])
        test_dict.add_multisegmented(["test_data/WS_test.txt"])
        self.assertEqual(test_dict.get_children_multisegmented("albo Argus"),
                         ['albo Argusa', 'albo Argusowi', 'albo Argusa', 'albo Argusem', 'albo Argusie',
                          'albo Argusie'])


if __name__ == '__main__':
    unittest.main()
