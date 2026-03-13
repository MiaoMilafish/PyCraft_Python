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
        time = await overworld.get_time()
        print(time)
    finally:
        await mc.close()

asyncio.run(main())