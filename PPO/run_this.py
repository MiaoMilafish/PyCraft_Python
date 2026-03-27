import asyncio
import torch
from pycraft import PyModClient
from env import MineEnv
from ppo_model import PPO
from train_ppo import PPOTrainer

async def main():
    client = PyModClient()
    await client.connect()

    try:
        level = client.overworld()
        agent = (await level.get_players())[0]

        env = MineEnv(level, agent)

        model = PPO(obs_dim=9, action_dim=5)
        trainer = PPOTrainer(model)

        for episode in range(200):

            states = []
            actions = []
            rewards = []
            log_probs = []
            values = []
            dones = []

            obs = await env.reset()

            for t in range(100):
                s = torch.tensor(obs, dtype=torch.float32)

                logits, value = model(s)
                dist = torch.distributions.Categorical(logits=logits)

                action = dist.sample()

                next_obs, reward, done = await env.step(action.item())

                states.append(s)
                actions.append(action)
                rewards.append(reward)
                log_probs.append(dist.log_prob(action))
                values.append(value.squeeze())
                dones.append(done)

                obs = next_obs

                if done:
                    break

            # bootstrap
            _, last_value = model(torch.tensor(obs, dtype=torch.float32))
            values.append(last_value.squeeze())

            advantages = trainer.compute_gae(rewards, values, dones)
            returns = advantages + torch.stack(values[:-1])

            trainer.update(
                torch.stack(states),
                torch.stack(actions),
                torch.stack(log_probs).detach(),
                returns.detach(),
                advantages.detach()
            )

            print(f"Episode {episode}, reward={sum(rewards)}")

    finally:
        await client.close()

asyncio.run(main())