import asyncio
import random

class MineEnv:
    def __init__(self, level, agent, size=10):
        self.level = level
        self.agent = agent
        self.size = size
        self.origin = (0, 64, 0)
        self.n_actions = 5

    async def reset(self):
        ox, oy, oz = self.origin
        # 清空
        await self.level.set_blocks(
            ox-1, oy, oz-1,
            ox+self.size, oy+3, oz+self.size,
            "minecraft:air"
        )

        # 生成矿井
        self.grid = {}
        for x in range(self.size):
            for z in range(self.size):
                r = random.random()
                if r < 0.1:
                    block = "minecraft:lava"
                elif r < 0.2:
                    block = "minecraft:tripwire"
                elif r < 0.35:
                    block = "minecraft:diamond_ore"
                else:
                    block = "minecraft:stone"
                self.grid[(x,z)] = block
                await self.level.set_block(
                    ox+x, oy, oz+z, block
                )

        self.agent_pos = [0, 0]
        self.done = False
        await self._teleport()
        return await self._get_obs()

    async def _teleport(self):
        ox, oy, oz = self.origin
        x,z = self.agent_pos
        await self.agent.teleport(ox+x, oy+1, oz+z)

    async def _get_obs(self):
        # 局部3x3观察
        x,z = self.agent_pos
        obs = []
        for dx in [-1,0,1]:
            for dz in [-1,0,1]:
                pos = (x+dx, z+dz)
                block = self.grid.get(pos, "wall")
                # 编码
                if block == "minecraft:stone": obs.append(0)
                elif block == "minecraft:diamond_ore": obs.append(1)
                elif block == "minecraft:lava": obs.append(2)
                elif block == "minecraft:tripwire": obs.append(3)
                else: obs.append(-1)
        return obs

    async def step(self, action):
        reward = -0.01

        x,z = self.agent_pos

        # 移动
        if action == 0: x += 1
        elif action == 1: x -= 1
        elif action == 2: z += 1
        elif action == 3: z -= 1

        # 边界
        if (x,z) not in self.grid:
            reward = -1
        else:
            self.agent_pos = [x,z]

        # 挖矿
        if action == 4:
            pos = tuple(self.agent_pos)
            block = self.grid.get(pos)

            if block == "minecraft:diamond_ore":
                reward = +2
                self.grid[pos] = "minecraft:air"

                ox, oy, oz = self.origin
                await self.level.set_block(
                    ox+pos[0], oy, oz+pos[1],
                    "minecraft:air"
                )

            elif block == "minecraft:stone":
                reward = +0.2
                self.grid[pos] = "minecraft:air"

        # 危险
        block = self.grid.get(tuple(self.agent_pos))

        if block == "minecraft:lava":
            reward = -5
            self.done = True

        if block == "minecraft:tripwire":
            reward = -2

        await self._teleport()

        obs = await self._get_obs()

        return obs, reward, self.done