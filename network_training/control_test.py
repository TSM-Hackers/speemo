"""Control script for using the module"""
import pickle
import sentiment_toolkit as st
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.optim as optim


def test_network(net, test_dataset, test_labels):
    """Run the accuracy on the test set"""
    net.eval()
    score = 0
    tries = 0

    for iteration in range(len(test_dataset)):
        inputs = test_dataset[iteration]
        local_labels = test_labels[iteration]

        inputs = Variable(inputs)
        local_labels = Variable(local_labels)

        outputs = nn.functional.softmax(net(inputs))
        m, am = torch.max(outputs.data, dim=1)

        result = am == local_labels.data
        score += result.numpy()[0]
        tries += 1

        if (iteration % 1000 == 0) and (iteration != 0):
            print("Going through iteration", iteration)

    return score / tries, score, tries


if (__name__ == "__main__"):
    filename = "dataset/test_dataset.pkl"
    with open(filename, "rb") as fp:
        data, labs, labels2names = pickle.load(fp)

    filename = "trained_model.pkl"
    with open(filename, "rb") as fp:
        net = pickle.load(fp)
        net.eval()

    n_input, n_output = data[0].size(2), int(labs.max() + 1)
    n_hidden = net.n_hidden
    n_layers = net.n_layers

    print(net)

    accuracy, score, tries = test_network(net, data, labs)
    print("Score:", score, "Tries:", tries, "Accuracy:", accuracy)
