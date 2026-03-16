import asyncio
from pycraft import PyModClient

async def main():
    mc = PyModClient()
    await mc.connect()
    try:
        overworld = mc.overworld()
        await overworld.set_block(0, 100, 0, "minecraft:diamond_block")
        block = await overworld.get_block(0,100,0)
        print(block)
        players = await overworld.get_players()
        print(players)
        player = players[0]
        # await player.move_to(120, 80, 120, 0.3)
        await player.teleport(120, 80, 120)
        pos = await player.get_pos()
        print(pos)
        time = await overworld.get_time()
        print(time)
    finally:
        await mc.close()

asyncio.run(main())