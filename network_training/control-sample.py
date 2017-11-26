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
    net.eval()
print(net)


sentence = ["I", "am", "really", "happy", "today"]
name, label = st.sample_network(net, sentence)
print(name, sentence)

sentence = ["I", "am", "really", "sad", "today"]
name, label = st.sample_network(net, sentence)
print(name, sentence)

sentence = ["I", "am", "worried", "we", "might", "not", "finish", "on", "time"]
name, label = st.sample_network(net, sentence)
print(name, sentence)
