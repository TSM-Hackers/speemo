"""Control script for using the module"""
import pickle
import time
import sentiment_toolkit as st
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.optim as optim
from control_test import test_network


filename = "dataset/train_dataset.pkl"
with open(filename, "rb") as fp:
    data, labs, labels2names = pickle.load(fp)

filename = "dataset/test_dataset.pkl"
with open(filename, "rb") as fp:
    data_test, labs_test, labels2names = pickle.load(fp)


n_input, n_output = data[0].size(2), int(labs.max() + 1)
n_hidden = 512
n_layers = 1

net = st.MySecondRNN(n_input, n_hidden, n_layers, n_output, drop_p=0.5)
# filename = "trained_model.pkl"
# with open(filename, "rb") as fp:
#     net = pickle.load(fp)
#     net.train()

print(net)
net.cuda()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=1e-3)

last_accuracy = 0
early_stop_counter = 0
for epoch in range(100):
    running_loss = 0
    optimizer.param_groups[0]["lr"] *= 0.9
    start = time.time()
    for iteration in range(len(data)):
        inputs = data[iteration]
        local_labels = labs[iteration]

        # inputs = Variable(inputs)
        # local_labels = Variable(local_labels)
        inputs = Variable(inputs.cuda())
        local_labels = Variable(local_labels.cuda())

        optimizer.zero_grad()
        outputs = net(inputs)

        loss = criterion(outputs, local_labels)
        loss.backward()

        optimizer.step()

        running_loss += loss.data[0]
        if (iteration % 1000 == 0) and (iteration != 0):
            print('(%d, %5d) loss: %.5e' %
                  (epoch, iteration, running_loss / 1000))
            running_loss = 0.0

    end = time.time()
    print("Epoch time: %.1fs" % (end - start))
    net.zero_grad()
    net.cpu()
    net.eval()

    filename = "trained_model.pkl"
    with open(filename, "wb") as fp:
        pickle.dump(net, fp)

    # Early stopping
    new_accuracy, *_ = test_network(net, data_test, labs_test)
    print("New acc:", new_accuracy, "Old acc:", last_accuracy)
    if new_accuracy < last_accuracy:
        early_stop_counter += 1
        print(early_stop_counter)
    else:
        early_stop_counter = 0

    last_accuracy = new_accuracy
    if early_stop_counter == 5:
        break

    net.train()
    net.cuda()
