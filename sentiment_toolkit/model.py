"""ML model for sentiment analysis"""

import torch
import torch.nn as nn
from torch.autograd import Variable


class MySecondRNN(nn.Module):
    """More involved RNN network"""

    def __init__(self, n_input, n_hidden, n_layers, n_output, drop_p=0.2):
        """Summary

        Parameters
        ----------
        n_input : int
            n of input features
        n_hidden : int
            size of the hidden layer
        n_layers : int
            number of hidden layers
        n_output : int
            n of output features
        """
        super().__init__()
        self.n_hidden = n_hidden
        self.n_layers = n_layers
        self.drop_p = drop_p

        self.RNN = nn.LSTM(n_input, n_hidden, n_layers, dropout=drop_p)
        self.dropout = nn.Dropout(p=drop_p)
        self.rnn2output = nn.Linear(n_hidden, n_output)

    def forward(self, x):
        """All of the steps forward

        Parameters
        ----------
        x : Variable(seq_len, batch_size, num_features)
            input variable

        Returns
        -------
        Variable
            final output of the network
        """
        seq_len, batch_size, num_features = x.size()
        if next(self.parameters()).is_cuda:
            h_0 = Variable(torch.zeros(self.n_layers, batch_size, self.n_hidden).cuda())
            c_0 = Variable(torch.zeros(self.n_layers, batch_size, self.n_hidden).cuda())
        else:
            h_0 = Variable(torch.zeros(self.n_layers, batch_size, self.n_hidden))
            c_0 = Variable(torch.zeros(self.n_layers, batch_size, self.n_hidden))
        out, *hidden = self.RNN(x, (h_0, c_0))
        # out, *hidden = self.RNN(x, h_0)

        output = self.dropout(out[-1])
        output = self.rnn2output(output)

        return output


class MyRNN(nn.Module):
    """SImple RNN network"""

    def __init__(self, n_input, n_hidden, n_output):
        """Summary

        Parameters
        ----------
        n_input : int
            n of input features
        n_hidden : int
            size of the hidden layer
        n_output : int
            n of output features
        """
        super().__init__()

        self.n_hidden = n_hidden

        self.inp2hidden = nn.Linear(n_input, n_hidden)
        self.hidden2hidden = nn.Linear(n_hidden, n_hidden)

        self.tanh = nn.functional.tanh

        self.hidden2out = nn.Linear(n_hidden, n_output)

    def single_step_forward(self, input, hidden):
        """Single step forward

        Parameters
        ----------
        input : Variable
            Input values
        hidden : Variable
            Hidden state from the previous timestep

        Returns
        -------
        Variable
            new_hidden state
        """

        new_hidden = self.inp2hidden(input) + self.hidden2hidden(hidden)
        new_hidden = self.tanh(new_hidden)

        return new_hidden

    def forward(self, x):
        """All of the steps forward

        Parameters
        ----------
        x : Variable(seq_len, batch_size, num_features)
            input variable

        Returns
        -------
        Variable
            final output of the network
        """

        hidden = self.initHidden()

        for i in range(x.size(0)):
            hidden = self.single_step_forward(x[i], hidden)

        output = self.hidden2out(hidden)

        return output

    def initHidden(self):
        """Initialize hidden units to zero

        Returns
        -------
        Variable(1, n_hidden)
            hidden units for the network
        """
        return Variable(torch.zeros(1, self.n_hidden))
