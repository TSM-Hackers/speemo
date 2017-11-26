"""Control script for using the module"""
import pickle
import sentiment_toolkit as st
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.optim as optim


filename = "trained_model.pkl"
with open(filename, "rb") as fp:
    net = pickle.load(fp)
print(net)


sentence = ['layin', 'n', 'bed', 'with', 'a', 'headache', 'ughhh', '...', 'waitin', 'on', 'your', 'call', '...']

name, label = st.sample_network(net, sentence)
print(name, label)
