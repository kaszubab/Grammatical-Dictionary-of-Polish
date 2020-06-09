from time import time
import os
import math

from src.dict import dictionary

if __name__ == '__main__':
    print("-----------------------Test szybkości biblioteki - część jednosegmentowa-----------------------")
    for i in [100, 300, 600, 900]:
        print("===============================================================================================")
        print("Rozmiar testowanego pliku: " + str(
            math.ceil(os.stat("test_file_" + str(i) + ".txt").st_size / 1024)) + "KB")

        number_of_lines = 0
        with open("test_file_" + str(i) + ".txt", 'r', encoding="utf8") as f:
            for line in f:
                number_of_lines += 1
        print("Ilość wpisów w testowanym pliku: ", number_of_lines)

        start_of_building = time()
        test_dict = dictionary.Dictionary(["test_file_" + str(i) + ".txt"])
        end_of_building = time()
        print("Czas budowy struktury: " + str(end_of_building - start_of_building) + "s")
        print("Średni czas trwania przetworzenia jednego wpisu: "
              + str((end_of_building - start_of_building) / number_of_lines))

        start_get_parent = time()
        test_dict.get_parent("Gdański")
        end_get_parent = time()
        print("Czas odpytania o rodzica: " + str(end_get_parent - start_get_parent) + "s")

        start_get_children = time()
        test_dict.get_parent("Gdański")
        end_get_children = time()
        print("Czas odpytania o dziecko: " + str(end_get_children - start_get_children) + "s")
