import requests
from bs4 import BeautifulSoup


def create_test_file(filename, iterations=100):
    file_test = open(filename, "w", encoding='utf8')
    number_of_entries = 0
    for i in range(1, iterations):
        entry = ""
        r = requests.get("http://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=" + str(i) + "&variant=1")
        if r.status_code != 403 and r.json()['result'] != "ok":
            continue

        soup = BeautifulSoup(r.json()['html'], 'html.parser')
        article = soup.select_one("div.article-header > h1").next_element
        word_type = soup.select_one("div.article-header > p").next_element
        if word_type.strip() != "rzeczownik":
            continue

        entry += article.strip()
        print(str(i) + " " + entry)
        entry += " :  AA:"
        word_varieties = soup.select("span.form")
        for word in word_varieties:
            entry += word.next_element.strip()
            entry += ":"

        entry += "\n"
        print(entry)
        file_test.write(entry)
        number_of_entries += 1

    print(number_of_entries)
    file_test.close()


if __name__ == '__main__':
    create_test_file("test_file.txt", iterations=5000)
