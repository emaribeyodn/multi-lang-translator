import sys
from typing import Tuple, List, Any

import requests
from bs4 import BeautifulSoup


def get_url(_source_language: str, _target_language: str, _word: str) -> str:
    """
    create an url with data needed
    """
    return f"https://context.reverso.net/translation/{_source_language.lower()}-{_target_language.lower()}/{_word}"


def get_webpage(_url: str, _session) -> str:
    """
    Make a http request to a given url
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = _session.get(_url, headers=headers, timeout=5)
    if r.status_code == 200:
        print(r.status_code, "OK")
        return r.text
    else:
        return False


def extract_data(_page: str) -> Tuple[List, List, List]:
    """
    Extract from html code translations and example sentences
    """
    soup = BeautifulSoup(_page, 'lxml')

    word_translations = soup.select("div#translations-content > a.translation")
    word_translations = [i.text for i in word_translations]
    word_translations = [i.strip('\r\n').strip() for i in word_translations]
    word_translations = [i for i in word_translations if i != '']

    sources = soup.select("div.example > div.src.ltr > span")
    sources = [i.text for i in sources]
    sources = [i.strip('\r\n').strip() for i in sources]
    sources = [i for i in sources if i != '']

    targets = soup.select("div.example > div.trg > span")
    targets = [i.text for i in targets]
    targets = [i.strip('\r\n').strip() for i in targets]
    targets = [i for i in targets if i != '']

    return word_translations, sources, targets


def menu() -> None:
    """
    Print the menu of the program
    """
    menu_text: str = """
1. Arabic
2. German
3. English
4. Spanish
5. French
6. Hebrew
7. Japanese
8. Dutch
9. Polish
10. Portuguese
11. Romanian
12. Russian
13. Turkish
    """
    print(menu_text)


def save_data(_word: str, data: Any):
    with open(_word + '.txt', 'w') as f:
        f.write(data)


def handle_cli_args():
    if len(sys.argv) == 4:
        return sys.argv[1], sys.argv[2], sys.argv[3]


def main():
    translate_session = requests.Session()

    languages = ["Arabic", "German", "English", "Spanish", "French", "Hebrew", "Japanese", "Dutch", "Polish",
                 "Portuguese", "Romanian", "Russian", "Turkish"]

    source, target, word = handle_cli_args()

    if source.capitalize() not in languages:
        print(f"Sorry, the program doesn't support {source.capitalize()}")
        sys.exit()

    if target.capitalize() not in languages and target != 'all':
        print(f"Sorry, the program doesn't support {target.capitalize()}")
        sys.exit()

    results = ''

    if target == 'all':
        for lang in languages:
            if lang.lower() != source:
                url = get_url(source, lang, word)
                try:
                    page = get_webpage(url, translate_session)
                    if not page:
                        print(f"Sorry, unable to find {word}")
                        sys.exit()
                except (requests.ConnectionError, requests.Timeout):
                    print("Something wrong with your internet connection")
                word_translation, source_examples, target_examples = extract_data(page)

                results += f"{lang} Translations:" + '\n'
                results += word_translation[0] + '\n\n'
                results += f"{lang} Examples:" + '\n'
                results += source_examples[0] + '\n'
                results += target_examples[0] + '\n\n'
    else:
        url = get_url(source, target, word)
        try:
            page = get_webpage(url, translate_session)
            if not page:
                print(f"Sorry, unable to find {word}")
                sys.exit()
        except (requests.ConnectionError, requests.Timeout):
            print("Something wrong with your internet connection")
        word_translation, source_examples, target_examples = extract_data(page)

        results += f"{target.capitalize()} Translations:" + '\n'
        results += "\n".join(word_translation)
        results += '\n'

        results += f"{target.capitalize()} Examples:" + '\n'
        for s, t in zip(source_examples, target_examples):
            results += s + '\n'
            results += t + '\n\n'

    save_data(word, results)
    print(results)

    translate_session.close()


if __name__ == '__main__':
    main()
