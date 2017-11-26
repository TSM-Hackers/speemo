"""Functions for word embedding"""
import torchtext
import torch

"""
Load the GLOVE model as in https://nlp.stanford.edu/projects/glove/
The returned GloVe object includes attributes:

    stoi : string-to-index returns a dictionary of words to indexes
    itos : index-to-string returns an array of words by index
    vectors : returns the actual vectors. To get a word vector get the index to get the vector
"""
glove = torchtext.vocab.GloVe(name="twitter.27B", dim=100)


def word2vector(word):
    """Return a vector encoding the word

    Parameters
    ----------
    word : string
        A single word

    Returns
    -------
    torch tensor
        Tensor with an encoded word
    """
    return glove.vectors[glove.stoi[word]]


def vector2word(vector):
    """Return a string given a vector, really slow

    Parameters
    ----------
    vector : torch Tensor
        vector to be changed

    Returns
    -------
    str
        closest word to this vector
    """
    return find_closest_words(vector, n=1)[0][0]


def print_closest_words(*args, **kwargs):
    """Print the closest vectors to screen,
    see find_closest_words for details"""

    for example in find_closest_words(*args, **kwargs):
        print(example)


def find_closest_words(vec, n=10):
    """
    Find the closest words for a given vector, for fun mostly.
    See print_closest_words() for printout

    Parameters
    ----------
    vec : torch Tensor
        embedded word
    n : int
        number of closest words

    Returns
    -------
    TYPE
        Description
    """
    all_dists = [(w, torch.dist(vec, word2vector(w))) for w in glove.itos]
    sorted_dists = sorted(all_dists, key=lambda t: t[1])
    return sorted_dists[:n]
