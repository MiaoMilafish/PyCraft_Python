import asyncio
from pycraft import PyModClient

async def main():
    mc = PyModClient()
    await mc.connect()
    try:
        overworld = mc.overworld()

        players = await overworld.get_players()
        print(players)
        player = players[0]

        time = await overworld.get_time()
        print(time)

        await player.set_perspective(1)

        # 生成小猪
        pig_id = await overworld.spawn_entity(
            "minecraft:pig",
            120, 80, 120
        )
        print("Spawn pig:", pig_id)

        # 持续追逐
        while True:
            # 获取小猪位置
            px, py, pz = await pig_id.get_pos(pig_id)

            # 获取玩家位置（可选调试）
            player_pos = await player.get_pos()
            print("Player:", player_pos, "Pig:", (px, py, pz))

            # 玩家移动到小猪
            await player.move_to(px, py, pz, speed=0.25)

            # （可选）画轨迹
            await overworld.spawn_particle(px, py + 0.5, pz)

            await asyncio.sleep(0.05)  # 对齐20TPS

    finally:
        await mc.close()

asyncio.run(main())