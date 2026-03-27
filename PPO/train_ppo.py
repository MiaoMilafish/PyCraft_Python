import torch
import torch.optim as optim
import torch.nn.functional as F

class PPOTrainer:
    def __init__(self, model):
        self.model = model
        self.opt = optim.Adam(model.parameters(), lr=3e-4)

        self.gamma = 0.99
        self.lam = 0.95
        self.clip = 0.2

    def compute_gae(self, rewards, values, dones):
        adv = []
        gae = 0

        for i in reversed(range(len(rewards))):
            delta = rewards[i] + self.gamma * values[i+1] * (1-dones[i]) - values[i]
            gae = delta + self.gamma * self.lam * (1-dones[i]) * gae
            adv.insert(0, gae)

        return torch.tensor(adv)

    def update(self, states, actions, log_probs_old, returns, advantages):
        for _ in range(4):
            logits, values = self.model(states)
            dist = torch.distributions.Categorical(logits=logits)

            log_probs = dist.log_prob(actions)
            ratio = torch.exp(log_probs - log_probs_old)

            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1-self.clip, 1+self.clip) * advantages

            actor_loss = -torch.min(surr1, surr2).mean()
            critic_loss = F.mse_loss(values.squeeze(), returns)

            loss = actor_loss + 0.5 * critic_loss

            self.opt.zero_grad()
            loss.backward()
            self.opt.step()