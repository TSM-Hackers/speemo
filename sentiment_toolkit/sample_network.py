"""Control script for using the module"""
import torch
from torch.autograd import Variable
from .embedding_data import embed_sentence

labels2names = ['neutral', 'happy', 'sad', 'surprise', 'anger', 'fear']


def sample_network(net, sentence):
    """Get an emotional response given a sentence

    Parameters
    ----------
    net : torch.nn.model
        The network that is used ot classicy emotions
    sentence : list(str)
        sentence in form of

    Returns
    -------
    str
        String name of the emotion

    np.array
        probability distribution over the emotions
    """
    inputs = embed_sentence(sentence)
    inputs = Variable(inputs)
    outputs = torch.nn.functional.softplus(net(inputs))
    m, am = torch.max(outputs.data, dim=1)

    output_label = am.numpy()[0]
    outputs /= torch.norm(outputs)

    return labels2names[output_label], outputs.data.numpy()[0]
