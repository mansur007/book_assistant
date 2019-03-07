import nltk
from nltk.corpus import wordnet as wn
from nltk.tag import map_tag  # to simplify part-of-speech tagging
# to download 'wordnet' package do:
    # >>> import nltk
    # >>> nltk.download('wordnet')
from google.cloud import translate
from PyDictionary import PyDictionary
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=\
    "/data/pycharm_projects/audiobook_assistant/audiobook-assistant-9703181ebcfe.json"


class Dictionary(object):
    def __init__(self):
        self.dictionary = PyDictionary()
        self.translator = translate.Client()

    def translate(self, phrase, targlang):
        # return self.translator.translate(phrase, language)
        return self.translator.translate(phrase, target_language=targlang)

    def define(self, target_word, context_utterance):
        utt_tokenized = nltk.word_tokenize(context_utterance)
        utt_tagged = nltk.pos_tag(utt_tokenized)
        simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in utt_tagged]
        pos = 'UNKNOWN'
        for token, tag in simplifiedTags:
            if token == target_word:
                pos = tag
                pos = pos.lower().capitalize()  # to make it same form as pydictionary's
                break

        full_definition = self.dictionary.meaning(target_word)
        try:
            relevant_definition = full_definition[pos]
        except KeyError:
            # pos will be the first key in the definition dictionary
            pos = next(iter(full_definition))
            relevant_definition = full_definition[pos]

        return relevant_definition, pos

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