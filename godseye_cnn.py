# -*- coding: utf-8 -*-
"""GodsEye-CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VNo3iLVUCPWDwR59CzMFVQlJoQOoQRFl

# An Initial Model

First attempt at God's Eye

**IMPORTS:**
"""

!pip install torchviz
!pip install pycoco
from torch.utils.data.sampler import SubsetRandomSampler
from torch.autograd import Variable
from torchviz import make_dot
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import torch.optim as optim
import gdown

import matplotlib.pyplot as plt
import numpy as np # we always love numpy
import time
import json

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
import cv2
from collections import Counter
from skimage.color import rgb2lab, deltaE_cie76
import os

"""**DOWNLOADS AND EXTRACTION:**"""

!mkdir /data
!mkdir '/all_data/'

gdown.download('https://drive.google.com/uc?id=15q_VHXzFxdi-xj_0XTMsOzur5Vd7iaQe&export=download',
               '/content/test_data.zip',
               quiet=False)

!unzip -qq 'test_data.zip' -d '/data'

states = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado',
           'Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho',
           'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine',
           'Maryland','Massachusetts','Michigan','Minnesota','Mississippi',
           'Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey',
           'New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma',
           'Oregon','Pennsylvania', 'Rhode Island','South Carolina','South Dakota',
           'Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia',
           'Wisconsin','Wyoming']

for i in range(11,50):
  path = '/all_data/' + states[i] + '/'
  print(path)
  os.mkdir(path)

"""```
```

# Pre-processing
"""

from PIL import Image

states = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado',
           'Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho',
           'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine',
           'Maryland','Massachusetts','Michigan','Minnesota','Mississippi',
           'Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey',
           'New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma',
           'Oregon','Pennsylvania', 'Rhode Island','South Carolina','South Dakota',
           'Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia',
           'Wisconsin','Wyoming']

path1 = '/data/test_data/'


for i in range(0,50):
  state = states[i]
  listing = os.listdir(path1 + state + '/')  
  path2 = '/all_data/' + state + '/'
  for full_path in listing: 
    if full_path[-3:len(full_path)] == 'jpg':
      #print(path1 + state + '/' + full_path)
      img = cv2.imread(path1 + state + '/' + full_path)
      img_resized = cv2.resize(img, (128, 128))
      plt.imshow(img_resized)
      cv2.imwrite(path2 + full_path, img_resized)
      #print(path2 + full_path)

# img = cv2.imread('/all_data/2009_i1P25xWKoV-OURYEj-4hFA_270.jpg')
# plt.imshow(img)

import imageio
ext = ('.jpg','.png')

np.random.seed(0)
random = np.random.random(89986) #500027 for 10K
train_values = np.argwhere(random < 0.9).squeeze(1)
test_values = np.argwhere(random >= 0.9).squeeze(1)
print(random)
print(train_values)

# a = [0,0,0,1,0,1,1,0]

# print(test_values.squeeze(1))
# print(train_values.size)
# print(test_values.size)

# all_data[0][0].tolist()

# all_data

# import math
# tree_thr = [30,130,30]
# is_tree = []
# avg_color = []

# for i in range(10):
#   image = all_data[i][0].tolist()
#   avg_color = [np.mean(image[0]),np.mean(image[1]),np.mean(image[2])]
#   if avg_color[0] >= tree_thr[0] and avg_color[1] >= tree_thr[1] and avg_color[2] >= tree_thr[2]:
#     is_tree[i] = 1
#   else:
#     is_tree[i] = 0

# from PIL import Image

# def compute_average_image_color(img):
#     width, height = img.size

#     r_total = 0
#     g_total = 0
#     b_total = 0

#     count = 0
#     for x in range(0, width):
#         for y in range(0, height):
#             r, g, b = img.getpixel((x,y))
#             r_total += r
#             g_total += g
#             b_total += b
#             count += 1

#     return (r_total/count, g_total/count, b_total/count)

# img = Image.open('/data/Alabama/2007__0fIoN5jzi7jWQuXnda1Lg_0.jpg')
# #img = img.resize((50,50))  # Small optimization
# average_color = compute_average_image_color(img)
# print(average_color)

# Data set information
image_dims = 3, 128, 128

# n_training_samples = []
# n_test_samples = []

classes = ('Alabama','Alaska','Arizona','Arkansas','California','Colorado',
           'Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho',
           'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine',
           'Maryland','Massachusetts','Michigan','Minnesota','Mississippi',
           'Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey',
           'New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma',
           'Oregon','Pennsylvania', 'Rhode Island','South Carolina','South Dakota',
           'Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia',
           'Wisconsin','Wyoming')

# divratio = [.9,.8,.7,.6]
# for i in range(4):
#   n_training_samples[i] = divratio[i]*2000*50
#   n_test_samples[i] = (1-divratio[i])*2000*50
  
n_training_samples = 900*50 # How many training images to use
n_test_samples = 50*50 # How many test images to use

# Load the training set
all_data = torchvision.datasets.DatasetFolder(
    root='/all_data', loader=imageio.imread, extensions=ext, transform=transforms.ToTensor(), target_transform=None, is_valid_file=None)
train_sampler = SubsetRandomSampler(
    np.arange(n_training_samples, dtype=np.int64))
test_sampler = SubsetRandomSampler(np.arange(n_test_samples, dtype=np.int64))
#classes = train_set._find_classes('/data')[0]

#Load the test set
# test_set = torchvision.datasets.DatasetFolder(
#     root='/data', loader=imageio.imread, extensions=ext, transform=transforms.ToTensor(), target_transform=None, is_valid_file=None)

from torch.utils.data import Dataset
import torch

class SplitData(Dataset):
    def __init__(self, data, train_ind, test_ind, is_train):
        super(SplitData, self).__init__()
        
        self.data = data
        self.is_train = is_train
        self.train_ind= train_ind
        self.test_ind = test_ind
#         self.targets = np.concatenate((0*np.ones(tower.shape[0]), 1*np.ones(bear.shape[0])))
#         self.classes = ['tower', 'bear']
    
    def __len__(self):
      return self.train_ind.size if self.is_train else self.test_ind.size
    
    def __getitem__(self, index):
      if self.is_train:
        return self.data[self.train_ind[index]]
      if not self.is_train:
        return self.data[self.test_ind[index]]

train_set = SplitData(all_data, train_values, test_values, True)
test_set = SplitData(all_data, train_values, test_values, False)
# train_set[200]

# quick_draw_data = SplitData(tower, bear)

# im, target = quick_draw_data[0]
# plt.imshow(im, cmap='gray')
# plt.show()

#train_set.root = '/content/Alabama'



# print(train_sampler.indices)
# print(test_sampler.indices)

"""**IMAGE DISPLAY:**"""

def disp_image(image, class_idx, predicted=None):
    # need to reorder the tensor dimensions to work properly with imshow
    plt.imshow(image.transpose(0,2).transpose(0,1))
    plt.axis('off')
    if predicted:
        plt.title("Actual: " + classes[class_idx] + "     Predicted: " + classes[predicted])
    else:
        plt.title("Actual: " + classes[class_idx])
    plt.show()

#print("training set input data shape", train_set.data.shape)
#print("Number of training outputs", len(train_set.targets))
x, y = train_set[9000]
disp_image(x,y)
print(x.shape)

x, y = test_set[3000]
disp_image(x,y)
print(x.shape)

"""**UNDERSTANDING THE DATA:**"""

# import seaborn as sns

# sns.countplot(train_set.targets)
# plt.xticks(ticks=range(10), labels=classes)
# plt.show()

"""```
```

# Building the Network

**Network Class:**
"""

class MyCNN(nn.Module):
    # The init funciton in Pytorch classes is used to keep track of the parameters of the model
    # specifically the ones we want to update with gradient descent + backprop
    # So we need to make sure we keep track of all of them here
    def __init__(self):
        super(MyCNN, self).__init__()
        # layers defined here

        # Make sure you understand what this convolutional layer is doing.
        # E.g., considering looking at help(nn.Conv2D).  Draw a picture of what
        # this layer does to the data.

        # note: image_dims[0] will be 3 as there are 3 color channels (R, G, B)
        num_kernels = 16
        self.conv1 = nn.Conv2d(image_dims[0], num_kernels, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(num_kernels, num_kernels*2, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(num_kernels*2, num_kernels*4, kernel_size=3, stride=1, padding=1)

        # Make sure you understand what this MaxPool2D layer is doing.
        # E.g., considering looking at help(nn.MaxPool2d).  Draw a picture of
        # what this layer does to the data.

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)

        # maxpool_output_size is the total amount of data coming out of that
        # layer.  We have an exercise that asks you to explain why the line of
        # code below computes this quantity.
        self.maxpool_output_size = int(num_kernels*4 * (image_dims[1] / 8) * (image_dims[2] / 8))

        # Add on a fully connected layer (like in our MLP)
        # fc stands for fully connected
        fc1_size = 256
        self.fc1 = nn.Linear(self.maxpool_output_size, fc1_size)

        # we'll use this activation function internally in the network
        self.activation_func = torch.nn.ReLU()

        # Convert our fully connected layer into outputs that we can compare to the result
        fc2_size = len(classes)
        self.fc2 = nn.Linear(fc1_size, fc2_size)
        
        #fc3
        fc3_size = len(classes)
        self.fc3 = nn.Linear(fc2_size, fc3_size)
        
        #fc4
#         fc4_size = len(classes)
#         self.fc4 = nn.Linear(fc3_size, fc4_size)

        # Note: that the output will not represent the probability of the
        # output being in each class.  The loss function we will use
        # `CrossEntropyLoss` will take care of convering these values to
        # probabilities and then computing the log loss with respect to the
        # true label.  We could break this out into multiple steps, but it turns
        # out that the algorithm will be more numerically stable if we do it in
        # one go.  We have included a cell to show you the documentation for
        # `CrossEntropyLoss` if you'd like to check it out.
        
    # The forward function in the class defines the operations performed on a given input to the model
    # and returns the output of the model
    def forward(self, x):
        x = self.conv1(x)
        x = self.pool(x)
        x = self.activation_func(x)
        x = self.conv2(x)
        x = self.pool(x)
        x = self.activation_func(x)
        x = self.conv3(x)
        x = self.pool(x)
        x = self.activation_func(x)
        # this code flattens the output of the convolution, max pool,
        # activation sequence of steps into a vector
        x = x.view(-1, self.maxpool_output_size)
        x = self.fc1(x)
        x = self.activation_func(x)
        x = self.fc2(x)
        x = self.activation_func(x)
        x = self.fc3(x)
#         x = self.fc4(x)
        return x

    # The loss function (which we chose to include as a method of the class, but doesn't need to be)
    # returns the loss and optimizer used by the model
    def get_loss(self, learning_rate):
      # Loss function
      loss = nn.CrossEntropyLoss()
      # Optimizer, self.parameters() returns all the Pytorch operations that are attributes of the class
      optimizer = optim.Adam(self.parameters(), lr=learning_rate)
      return loss, optimizer

"""**Model the Network:**"""

def visualize_network(net):
    # Visualize the architecture of the model
    # We need to give the net a fake input for this library to visualize the architecture
    fake_input = Variable(torch.zeros((1,image_dims[0], image_dims[1], image_dims[2]))).to(device)
    outputs = net(fake_input)
    # Plot the DAG (Directed Acyclic Graph) of the model
    return make_dot(outputs, dict(net.named_parameters()))

# Define what device we want to use
device = 'cuda' # 'cpu' if we want to not use the gpu
# Initialize the model, loss, and optimization function
net = MyCNN()
# This tells our model to send all of the tensors and operations to the GPU (or keep them at the CPU if we're not using GPU)
net.to(device)

visualize_network(net)

"""**Train the model:**"""

# Define training parameters
batch_size = 32
learning_rate = 1e-3
n_epochs = 10
# Get our data into the mini batch size that we defined
train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch_size,
                                           sampler=train_sampler, num_workers=2)
test_loader = torch.utils.data.DataLoader(
    test_set, batch_size=100, sampler=test_sampler, num_workers=2)

def train_model(net):
    """ Train a the specified network.

        Outputs a tuple with the following four elements
        train_hist_x: the x-values (batch number) that the training set was 
            evaluated on.
        train_loss_hist: the loss values for the training set corresponding to
            the batch numbers returned in train_hist_x
        test_hist_x: the x-values (batch number) that the test set was 
            evaluated on.
        test_loss_hist: the loss values for the test set corresponding to
            the batch numbers returned in test_hist_x
    """ 
    loss, optimizer = net.get_loss(learning_rate)
    # Define some parameters to keep track of metrics
    print_every = 20
    idx = 0
    train_hist_x = []
    train_loss_hist = []
    test_hist_x = []
    test_loss_hist = []

    training_start_time = time.time()
    # Loop for n_epochs
    for epoch in range(n_epochs):
        running_loss = 0.0
        start_time = time.time()

        for i, data in enumerate(train_loader, 0):

            # Get inputs in right form
            inputs, labels = data
            inputs, labels = Variable(inputs).to(device), Variable(labels).to(device)
            
            # In Pytorch, We need to always remember to set the optimizer gradients to 0 before we recompute the new gradients
            optimizer.zero_grad()

            # Forward pass
            outputs = net(inputs)
            
            # Compute the loss and find the loss with respect to each parameter of the model
            loss_size = loss(outputs, labels)
            loss_size.backward()
            
            # Change each parameter with respect to the recently computed loss.
            optimizer.step()

            # Update statistics
            running_loss += loss_size.data.item()
            
            # Print every 20th batch of an epoch
            if (i % print_every) == print_every-1:
                print("Epoch {}, Iteration {}\t train_loss: {:.2f} took: {:.2f}s".format(
                    epoch + 1, i+1,running_loss / print_every, time.time() - start_time))
                # Reset running loss and time
                train_loss_hist.append(running_loss / print_every)
                train_hist_x.append(idx)
                running_loss = 0.0
                start_time = time.time()
            idx += 1

        # At the end of the epoch, do a pass on the test set
        total_test_loss = 0
        for inputs, labels in test_loader:

            # Wrap tensors in Variables
            inputs, labels = Variable(inputs).to(device), Variable(labels).to(device)

            # Forward pass
            test_outputs = net(inputs)
            test_loss_size = loss(test_outputs, labels)
            total_test_loss += test_loss_size.data.item()
        test_loss_hist.append(total_test_loss / len(test_loader))
        test_hist_x.append(idx)
        print("Validation loss = {:.2f}".format(
            total_test_loss / len(test_loader)))

    print("Training finished, took {:.2f}s".format(
        time.time() - training_start_time))
    return train_hist_x, train_loss_hist, test_hist_x, test_loss_hist

len(train_set)

train_hist_x, train_loss_hist, test_hist_x, test_loss_hist = train_model(net)

"""**Loss over time:**"""

plt.plot(train_hist_x[5:],train_loss_hist[5:])
plt.plot(test_hist_x[1:],test_loss_hist[1:])
plt.legend(['train loss', 'validation loss'])
plt.xlabel('Batch number')
plt.ylabel('Loss')
plt.show()

def examine_label(idx):
    image, label = test_set[idx]
    class_scores = net(Variable(image.unsqueeze(0)).to(device))
    prediction = np.argmax(class_scores.cpu().detach().numpy())
    disp_image(image, label, prediction)

examine_label(2050)

n_correct = 0
n_total = 0
for i, data in enumerate(train_loader, 0):
    # Get inputs in right form
    inputs, labels = data
    inputs, labels = Variable(inputs).to(device), Variable(labels).to(device)

    # Forward pass
    outputs = net(inputs)
    n_correct += np.sum(np.argmax(outputs.cpu().detach().numpy(), axis=1) == labels.cpu().numpy())
    n_total += labels.shape[0]
print("Training accuracy is", n_correct/n_total)

def get_accuracy(net, loader):
    n_correct = 0.0
    n_total = 0.0
    for i, data in enumerate(loader, 0):
        # Get inputs in right form
        inputs, labels = data
        inputs, labels = Variable(inputs).to(device), Variable(labels).to(device)

        # Forward pass
        outputs = net(inputs)
        n_correct += np.sum(np.argmax(outputs.cpu().detach().numpy(), axis=1) == labels.cpu().numpy())
        n_total += labels.shape[0]
    return n_correct/n_total
print("Train accuracy is", get_accuracy(net, train_loader))
print("Test accuracy is", get_accuracy(net, test_loader))
