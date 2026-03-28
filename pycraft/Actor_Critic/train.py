import torch
import torch.nn.functional as F
import torch.optim as optim
import asyncio


def state_to_tensor(state, max_len=64):
    """
    把 tuple state 转成固定长度 tensor（padding）
    """
    s = list(state)
    if len(s) < max_len:
        s += [0] * (max_len - len(s))
    else:
        s = s[:max_len]
    return torch.tensor(s, dtype=torch.float32)

async def train(env, model, episodes=300):
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    gamma = 0.99
    for ep in range(episodes):
        state = await env.reset()
        total_reward = 0
        for step in range(200):
            s = state_to_tensor(state)
            logits, value = model(s)
            probs = torch.softmax(logits, dim=-1)
            dist = torch.distributions.Categorical(probs)
            action = dist.sample()
            next_state, reward, done = await env.step(action.item())
            total_reward += reward

            # TD target
            with torch.no_grad():
                next_s = state_to_tensor(next_state)
                _, next_value = model(next_s)
            td_target = reward + gamma * next_value * (1 - int(done))
            advantage = td_target - value

            # loss
            actor_loss = -dist.log_prob(action) * advantage.detach()
            critic_loss = F.mse_loss(value, td_target)
            loss = actor_loss + critic_loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            state = next_state

            if done:
                break

        print(f"[Episode {ep}] reward={total_reward}")