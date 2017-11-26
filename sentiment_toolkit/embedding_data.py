"""Functions for embedding the dataset"""
import torch
from .embedding import *


def embed_sentence(sentence_list):
    """Given a list of strings, return a tensor

    Parameters
    ----------
    sentence_list : list(str)
        sentence provided as al ist of strings

    Returns
    -------
    Tensor(seq_length, batch_size=1, num_features)
        tensor with an encoded sentence, second dim is a dummy
        If no words could be embedded, returns None
    """
    tens = torch.Tensor()
    for word in sentence_list:
        try:
            vector = word2vector(word)
        except KeyError:
            continue
        tens = torch.cat((tens, vector.unsqueeze(0)), dim=0)

    if (len(tens) == 0):
        return None

    tens.unsqueeze_(1)
    return tens


def embed_dataset(data, labels):
    """Embed a whold dataset

    Parameters
    ----------
    data : list of list(str)
        dataset, a list of sentences
    labels : list(int)
        labels, a list of them

    Returns
    -------
    list(Tensors)
        list of tensors, each of them with
        dims = (seq_length, batch_size=1, num_features)
    IntTensor
        tensor of labels
    """
    labs = []
    dataset = list()
    for i, sentence in enumerate(data):
        sentence_tensor = embed_sentence(sentence)
        if sentence_tensor is not None:
            dataset.append(sentence_tensor)
            labs.append(labels[i])
            # if i % 100 == 0:
            #     print(sentence, labels[i], labs[-1])

    labs = torch.LongTensor(labs).unsqueeze_(1)
    return dataset, labs
