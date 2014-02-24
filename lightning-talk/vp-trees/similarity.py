def shingle(word, n):
    '''
    More on shingling here: http://blog.mafr.de/2011/01/06/near-duplicate-detection/
    '''
    return set([word[i:i + n] for i in range(len(word) - n + 1)])

def jaccard(a, b):
    '''
    Jaccard similarity between two sets.

    Explanation here: http://en.wikipedia.org/wiki/Jaccard_index
    '''
    x, y = shingle(a, 3), shingle(b, 3)
    return 1.0 - (float(len(x & y) + 1) / float(len(x | y) + 1)) # Smoothing