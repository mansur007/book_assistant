import nltk
from nltk.corpus import wordnet as wn
# to download 'wordnet' package do:
    # >>> import nltk
    # >>> nltk.download('wordnet')
from google.cloud import translate
from PyDictionary import PyDictionary
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=\
    "/home/mans/pycharm_projects/audiobook_assistant/audiobook-assistant-9703181ebcfe.json"


class Dictionary(object):
    def __init__(self):
        self.dictionary = PyDictionary()
        self.translator = translate.Client()

    def translate(self, phrase, targlang):
        # return self.translator.translate(phrase, language)
        return self.translator.translate(phrase, target_language=targlang)

    def define(self, word):
        return self.dictionary.meaning(word)

    def find_synonym_of(self, word):
        return wn.synsets(word)


if __name__ == '__main__':
    d = Dictionary()
    word = 'goods'
    # translation = d.translate(word, 'ru')
    # print(u'Translation: {}'.format(translation['translatedText']))
    print(d.define(word))
    # print(d.find_synonym_of(word))
    # text = "I would like to thank everyone for your attention, and see you soon!"
    # tokens = nltk.word_tokenize(text)
    # print(nltk.pos_tag(tokens))