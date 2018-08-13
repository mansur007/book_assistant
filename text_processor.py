import Levenshtein as Lev


def cer(s1, s2):
    # character error rate (or edit distance)
    return Lev.distance(s1, s2)


def find_most_similar_word(word, excerpt):
    if isinstance(excerpt, str):
        excerpt = excerpt.split()
    elif not isinstance(excerpt, list):
        # assume it is string
        assert(isinstance(excerpt, str)), "'excerpt' argument is neither string nor list of words"
    assert(len(excerpt)), "length of word_list is zero"

    min_cer = float('inf')
    for w in excerpt:
        cer_distance = cer(word, w)
        if cer_distance < min_cer:
            best_match = w
            min_cer = cer_distance
    return best_match


def parse_command(command):
    word_list = command.split()
    print(word_list)
    for i in range(len(word_list)):
        word = word_list[i]
        phrase = []
        if cer(word, 'translate') <= 3:
            if i+1 == len(word_list):
                phrase.append('it')
                rest = []
            else:
                phrase.append(word_list[i+1])
                rest = word_list[i+2:]

            if len(rest) == 0:
                args = []
            else:
                args = []
                for j in range(len(rest)):
                    if cer(rest[j], 'into')==0 or cer(rest[j], 'to')==0:
                        args = rest[j+1:]
                        break
                    else:
                        phrase.append(rest[j])

            return {'func': 'translate', 'phrase': phrase, 'args': args}
        elif cer(word, 'synonym') <= 3:
            if i+2 >= len(word_list):  # just 'synonym of' will be regarded as 'synonym of it'
                phrase = ['it']
            else:
                phrase = word_list[i+2:]
            return {'func': 'synonym', 'phrase': phrase, 'args': []}
        # elif cer(word, 'spell') <= 1:
        #     if i+1 == len(word_list):
        #         phrase = ['it']
        #     else:
        #         phrase = word_list[i+1:]
        #     return {'func': 'spell', 'phrase': phrase, 'args': []}
        # elif cer(word, 'what') <= 1:
        #     if cer(word_list[i+2], 'synonym') <= 2:
        #         if i + 4 >= len(word_list):  # just 'synonym of' will be regarded as 'synonym of it'
        #             phrase = ['it']
        #         else:
        #             phrase = word_list[i + 4:]
        #         return {'func': 'synonym', 'phrase': phrase, 'args': []}
        # elif cer(word, 'find') <= 1:
        #     if cer(word_list[i+1], 'synonym') <= 2:
        #         if i + 3 >= len(word_list):  # just 'synonym of' will be regarded as 'synonym of it'
        #             phrase = ['it']
        #         else:
        #             phrase = word_list[i + 3:]
        #         return {'func': 'synonym', 'phrase': phrase, 'args': []}
        elif cer(word, 'define') <= 3:
            if i+1 == len(word_list):
                phrase = ['it']
            else:
                phrase = word_list[i+1:]
            return {'func': 'define', 'phrase': phrase, 'args': []}
        else:
            return {'func': 'unknown'}


def test_cer():
    s1 = 'seek'
    s2 = 'sick'
    print("cer({}, {}): {}".format(s1, s2, cer(s1, s2)))

if __name__ == '__main__':
    # test_cer()
    print(parse_command('define conor'))
    print(find_most_similar_word('conor', 'He was sitting still in the corner'))