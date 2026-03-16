import asyncio
import heapq
import time
from pycraft import PyModClient

def create_maze():
    return [[0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 1, 1, 0, 0],
            [0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 0, 1, 1, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 0, 0, 1, 0]]

async def draw_maze(level, maze, base_x, base_y, base_z):
    rows = len(maze)
    cols = len(maze[0])
    stone = "minecraft:stone"
    air = "minecraft:air"
    # 清空区域
    await level.set_blocks(
        base_x - 1, base_y - 3, base_z - 1,
        base_x + rows + 1, base_y + 5, base_z + cols + 1,
        air
    )
    # 外墙
    await level.set_blocks(base_x-1, base_y-3, base_z-1, base_x+rows, base_y, base_z-1, stone)
    await level.set_blocks(base_x-1, base_y-3, base_z+cols, base_x+rows, base_y, base_z+cols, stone)
    await level.set_blocks(base_x-1, base_y-3, base_z, base_x-1, base_y, base_z+cols, stone)
    await level.set_blocks(base_x+rows, base_y-3, base_z, base_x+rows, base_y, base_z+cols, stone)
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 1:
                await level.set_blocks(
                    base_x + r, base_y - 3, base_z + c,
                    base_x + r, base_y, base_z + c,
                    stone
                )

def dijkstra(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    pq = [(0, start)]
    dist = {start: 0}
    parent = {start: None}
    visited = set()
    while pq:
        cost, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        if cur == end:
            path = []
            while cur:
                path.append(cur)
                cur = parent[cur]
            return path[::-1]
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = cur[0]+dr, cur[1]+dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                new_cost = cost + 1
                if (nr,nc) not in dist or new_cost < dist[(nr,nc)]:
                    dist[(nr,nc)] = new_cost
                    parent[(nr,nc)] = cur
                    heapq.heappush(pq, (new_cost, (nr,nc)))
    return []

async def show_path(level, player, path, block_id, base_x, base_y, base_z):
    for r, c in path:
        x = base_x + r
        z = base_z + c
        await level.set_block(x, base_y-1, z, block_id)
        await player.teleport(x, base_y + 1, z)
        await asyncio.sleep(0.3)

async def main():
    mc = PyModClient()
    await mc.connect()
    try:
        level = mc.overworld()
        players = await level.get_players()
        player = players[0]
        x, y, z = await player.get_pos()
        base_x = int(x)
        base_y = int(y)
        base_z = int(z)
        maze = create_maze()
        await draw_maze(level, maze, base_x, base_y, base_z)
        start = (0, 0)
        end = (9, 9)
        path = dijkstra(maze, start, end)
        gold = "minecraft:gold_block"
        await show_path(level, player, path, gold, base_x, base_y, base_z)
    finally:
        await mc.close()

if __name__ == "__main__":
    asyncio.run(main())