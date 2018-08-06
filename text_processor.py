import Levenshtein as Lev


def cer(s1, s2):
    # character error rate (or edit distance)
    return Lev.distance(s1, s2)



if __name__ == '__main__':
    s1 = 'seek'
    s2 = 'sick'
    print(cer(s1, s2))