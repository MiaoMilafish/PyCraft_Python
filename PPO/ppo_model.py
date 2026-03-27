import torch.nn as nn
import torch.nn.functional as F

class PPO(nn.Module):
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.fc = nn.Linear(obs_dim, 128)
        self.actor = nn.Linear(128, action_dim)
        self.critic = nn.Linear(128, 1)

    def forward(self, x):
        x = F.relu(self.fc(x))
        return self.actor(x), self.critic(x)