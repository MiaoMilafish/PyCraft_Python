import asyncio
from mc_env import Maze
from QLearning import QLearningTable
from pycraft import PyModClient


async def update(env, RL):
    for episode in range(100):
        observation = await env.reset()
        while True:
            # 选择动作（QLearning 不变）
            action = RL.choose_action(str(observation))
            # 与环境交互（必须 await）
            observation_, reward, done = await env.step(action)
            # 学习（同步）
            RL.learn(str(observation), action, reward, str(observation_))
            observation = observation_
            if done:
                break

async def main():
    client = PyModClient()
    await client.connect()
    try:
        level = client.overworld()
        players = await level.get_players()
        agent = players[0]
        env = Maze(client, level, agent)
        await env.build_maze()
        RL = QLearningTable(actions=list(range(env.n_actions)))
        await update(env, RL)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())