import asyncio

class Maze:
    def __init__(self, client, level, agent):
        self.client = client
        self.level = level
        self.agent = agent

        self.origin = (0, 64, 0)  # y抬高一点避免地下

        self.maze = [
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 1, 1, 0, 0],
            [0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 0, 1, 1, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 0, 0, 1, 0]
        ]

        self.rows = len(self.maze)
        self.cols = len(self.maze[0])

        self.start = (0, 0)
        self.goal = (9, 9)

        self.n_actions = 4

    # =========================
    # 构建迷宫
    # =========================
    async def build_maze(self):
        ox, oy, oz = self.origin

        # 清空区域
        await self.level.set_blocks(
            ox - 5, oy - 2, oz - 5,
            ox + 20, oy + 10, oz + 20,
            "minecraft:air"
        )

        # 地面 + 墙
        for r in range(self.rows):
            for c in range(self.cols):
                # 地面
                await self.level.set_block(
                    ox + r, oy, oz + c,
                    "minecraft:grass_block"
                )

                if self.maze[r][c] == 1:
                    # 墙
                    await self.level.set_blocks(
                        ox + r, oy + 1, oz + c,
                        ox + r, oy + 3, oz + c,
                        "minecraft:stone"
                    )

        # 外围墙
        await self.level.set_blocks(ox - 1, oy, oz - 1, ox + self.rows, oy + 3, oz - 1, "minecraft:stone")
        await self.level.set_blocks(ox - 1, oy, oz + self.cols, ox + self.rows, oy + 3, oz + self.cols, "minecraft:stone")
        await self.level.set_blocks(ox - 1, oy, oz, ox - 1, oy + 3, oz + self.cols, "minecraft:stone")
        await self.level.set_blocks(ox + self.rows, oy, oz, ox + self.rows, oy + 3, oz + self.cols, "minecraft:stone")

        # 终点
        gx, gz = self.goal
        await self.level.set_block(
            ox + gx, oy, oz + gz,
            "minecraft:gold_block"
        )

    # =========================
    # reset
    # =========================
    async def reset(self):
        self.agent_pos = self.start
        await self.teleport_agent()
        return self.agent_pos

    async def teleport_agent(self):
        x, z = self.agent_pos
        ox, oy, oz = self.origin

        await self.agent.teleport(
            ox + x,
            oy + 1,
            oz + z
        )

    # =========================
    # step（RL核心）
    # =========================
    async def step(self, action):
        x, z = self.agent_pos

        moves = {
            0: (0, -1),
            1: (0, 1),
            2: (-1, 0),
            3: (1, 0)
        }

        dx, dz = moves[action]
        nx, nz = x + dx, z + dz

        reward = -0.04
        done = False

        if nx < 0 or nx >= self.rows or nz < 0 or nz >= self.cols:
            reward = -1

        elif self.maze[nx][nz] == 1:
            reward = -1

        else:
            self.agent_pos = (nx, nz)
            await self.teleport_agent()

            if self.agent_pos == self.goal:
                reward = 1
                done = True

        await asyncio.sleep(0.2)
        return self.agent_pos, reward, done