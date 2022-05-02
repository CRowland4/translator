import sys
import argparse
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("target")
parser.add_argument("word")
args = parser.parse_args()


class Translator:

    def __init__(self):
        self.available_languages = {
            '1': 'Arabic',
            '2': 'German',
            '3': 'English',
            '4': 'Spanish',
            '5': 'French',
            '6': 'Hebrew',
            '7': 'Japanese',
            '8': 'Dutch',
            '9': 'Polish',
            '10': 'Portuguese',
            '11': 'Romanian',
            '12': 'Russian',
            '13': 'Turkish'
        }
        self.source_language = ''
        self.target_language = ''
        self.translation_word = ''
        self.request_response = None
        self.response_status = 0
        self.soup = None
        self.translated_words = []
        self.translation_examples = {
            'source examples': [],
            'target examples': []
        }
        self.file_content = ''

    def main(self):
        self._get_user_query()
        self._check_languages()

        if self.target_language == 'all':
            self._give_all_translations()
        else:
            self._give_single_translation(example_count=5)

        self._create_content_file()
        self._print_content()
        return

    def _get_user_query(self):
        self.source_language = args.source
        self.target_language = args.target
        self.translation_word = args.word
        return

    def _check_languages(self):
        """Checks that the requested languages are valid."""
        if self.source_language.title() not in self.available_languages.values():
            print(f"Sorry, the program doesn't support {self.source_language}")
            sys.exit()
        if self.target_language.title() not in self.available_languages.values() and self.target_language != 'all':
            print(f"Sorry, the program doesn't support {self.target_language}")
            sys.exit()

        return

    def _give_all_translations(self):
        """ Gives the requested translation in all available languages."""
        source = self.source_language  # This is so the next line doesn't go over PEP's character limit
        languages = [language for language in self.available_languages.values() if language != source.title()]

        for language in languages:
            self.target_language = language
            self._give_single_translation(example_count=1)
            self._reset_translations_attributes()

        return

    def _give_single_translation(self, example_count):
        """Gives the requested translation in the single specified language."""
        self._set_translation_response()
        self._update_response_status()

        if self.response_status == 200:
            pass
        elif self.response_status == 404:
            print(f"Sorry, unable to find {self.translation_word}")
            sys.exit()
        elif self.response_status >= 500:
            print("Something wrong with your internet connection")
            sys.exit()

        self._set_soup()
        self._update_translated_words()
        self._give_translation_words(example_count)
        self._update_translation_examples()
        self._give_translation_examples(example_count)
        return

    def _set_translation_response(self):
        """Sets the request_response object."""
        translation = f'{self.source_language.lower()}-{self.target_language.lower()}/{self.translation_word}'
        url = f'https://context.reverso.net/translation/{translation}'
        self.request_response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        return

    def _update_response_status(self):
        """Sets the response status code attribute."""
        self.response_status = self.request_response.status_code
        return

    def _set_soup(self):
        """Sets the soup attribute"""
        self.soup = BeautifulSoup(self.request_response.content, 'html.parser')
        return

    def _update_translated_words(self):
        """Updates the translated_words attribute by extracting the translated words from the response."""
        div = self.soup.find('div', id='translations-content')  # This is the div tag that contains the translated words
        a_tags = div.find_all('a')  # The translated words are contained within the 'a' tags

        for tag in a_tags:
            self.translated_words.append(tag.text.strip())

        return

    def _give_translation_words(self, count):
        """Prints the translations of the previously selected word."""
        content = f'{self.target_language} Translations:'
        self.file_content += content

        for word in self.translated_words[:count]:
            self.file_content += '\n' + word

        self.file_content += '\n\n'
        return

    def _update_translation_examples(self):
        """Updates the translation_examples attribute by extracting the examples from the response."""
        target_class = self._get_target_class()

        source_example_tags = self.soup.find_all('div', class_='src ltr')
        target_example_tags = self.soup.find_all('div', class_=target_class)

        for source_tag, target_tag in zip(source_example_tags, target_example_tags):
            self.translation_examples['source examples'].append(source_tag.text.strip())
            self.translation_examples['target examples'].append(target_tag.text.strip())

        return

    def _get_target_class(self):
        """Returns the CSS class for the current self.target_language."""
        if self.target_language not in ['Arabic', 'Hebrew']:
            return 'trg ltr'
        elif self.target_language == 'Arabic':
            return 'trg rtl arabic'
        elif self.target_language == 'Hebrew':
            return 'trg rtl'

    def _give_translation_examples(self, count):
        """Prints the translation sentences generated by the previously selected word to translate."""
        content = f'{self.target_language} Examples:'
        self.file_content += content

        source_list = self.translation_examples['source examples']
        target_list = self.translation_examples['target examples']
        for source_sentence, target_sentence in zip(source_list[:count], target_list[:count]):
            examples = f'{source_sentence}\n{target_sentence}\n'
            self.file_content += '\n' + examples

        self.file_content += '\n\n'

        return

    def _reset_translations_attributes(self):
        """Resets the translation attributes to empty lists."""
        self.translation_examples['source examples'] = []
        self.translation_examples['target examples'] = []
        self.translated_words = []
        return

    def _create_content_file(self):
        """Saves the translation content to a file."""
        with open(f'{self.translation_word}.txt', 'w', encoding='utf-8') as file:
            file.write(self.file_content)
        return

    def _print_content(self):
        """Prints out the result of the query."""
        print(self.file_content)
        return


my_translator = Translator()
my_translator.main()
