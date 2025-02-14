import torch
import torch.nn as nn
import torch.optim as optim
from Networks import MNIST_FPN
from utils import mnist_loaders, train_Jacobian_based_net
device = "cuda:1"
print('device = ', device)

seed = 1003
torch.manual_seed(seed)
save_dir = './results/'

# -----------------------------------------------------------------------------
# Network setup
# -----------------------------------------------------------------------------
contraction_factor = 0.5
lat_layers = 2
T = MNIST_FPN(lat_layers=lat_layers, num_channels=32,
              contraction_factor=contraction_factor,
              architecture='Jacobian').to(device)
num_classes = 10
eps = 1.0e-1
max_depth = 50

# -----------------------------------------------------------------------------
# Training settings
# -----------------------------------------------------------------------------
max_epochs = 100
learning_rate = 2e-4
weight_decay = 1e-6
optimizer = optim.Adam(T.parameters(), lr=learning_rate,
                      weight_decay=weight_decay)
lr_scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=100, gamma=1.0)
checkpt_path = './models/'
criterion = nn.CrossEntropyLoss()

print('weight_decay = ', weight_decay, ', learning_rate = ', learning_rate,
      ', eps = ', eps, ', max_depth = ', max_depth, 'contraction_factor = ',
      contraction_factor, 'optimizer = Adam')

# -----------------------------------------------------------------------------
# Load dataset
# -----------------------------------------------------------------------------
batch_size = 100
test_batch_size = 400

train_loader, test_loader = mnist_loaders(train_batch_size=batch_size,
                                          test_batch_size=test_batch_size)

# train network!
T = train_Jacobian_based_net(T, max_epochs, lr_scheduler, train_loader,
                       test_loader, optimizer, criterion, num_classes,
                       eps, max_depth, save_dir=save_dir)
