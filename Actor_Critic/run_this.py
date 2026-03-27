import asyncio
from pycraft import PyModClient
from env import BuildEnv
from model import ActorCritic
from train import train

async def main():
    client = PyModClient()
    await client.connect()
    try:
        level = client.overworld()
        players = await level.get_players()
        agent = players[0]
        env = BuildEnv(level, agent)
        # state_dim 要 >= state_to_tensor max_len
        model = ActorCritic(state_dim=64, action_dim=7)
        await train(env, model, episodes=200)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())