import asyncio

class BuildEnv:
    def __init__(self, level, agent):
        self.level = level
        self.agent = agent
        self.origin = (0, 64, 0)

        # 2x2x2 小房子
        self.target = {
            (0,0,0),(1,0,0),(0,0,1),(1,0,1),
            (0,1,0),(1,1,0),(0,1,1),(1,1,1),
        }

        self.reset_internal()

    def reset_internal(self):
        self.placed = set()
        self.agent_pos = [0, 0, 0]

    async def reset(self):
        self.reset_internal()
        ox, oy, oz = self.origin
        # 清空区域
        await self.level.set_blocks(
            ox-5, oy, oz-5,
            ox+5, oy+5, oz+5,
            "minecraft:air"
        )
        await self._teleport()
        return self._get_state()

    async def _teleport(self):
        ox, oy, oz = self.origin
        x,y,z = self.agent_pos
        await self.agent.teleport(ox+x, oy+y+1, oz+z)

    def _get_state(self):
        # 简化状态（可换 voxel）
        return tuple(self.agent_pos) + tuple(sorted(self.placed))

    async def step(self, action):
        reward = -0.02 # 每一步都有微小惩罚
        done = False
        x,y,z = self.agent_pos
        # 移动
        if action == 1: x += 1
        elif action == 2: x -= 1
        elif action == 3: z += 1
        elif action == 4: z -= 1
        elif action == 5: y += 1
        elif action == 6: y -= 1

        # 放方块
        elif action == 0:
            pos = tuple(self.agent_pos)
            if pos in self.target and pos not in self.placed:
                self.placed.add(pos)
                ox, oy, oz = self.origin
                await self.level.set_block(
                    ox+pos[0], oy+pos[1], oz+pos[2],
                    "minecraft:stone"
                )
                reward = 1 # 放在正确位置给奖励
            else:
                reward = -0.5 # 放在错误位置或重复放置
        self.agent_pos = [x,y,z]
        await self._teleport()

        # 完成判断
        if self.placed == self.target:
            reward = 10 # 全部完成
            done = True

        await asyncio.sleep(0.05)
        return self._get_state(), reward, done