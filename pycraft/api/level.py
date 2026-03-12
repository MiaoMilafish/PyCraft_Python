# pycraft/api/level.py
import asyncio

class Level:
    """
    维度类，保存对维度的引用
    """
    def __init__(self, client, name: str):
        self._client = client
        self.name = name  # 维度标识符，如 "minecraft:overworld"

    async def get_time(self) -> int:
        """
        获取该维度的当前游戏时间（以 tick 为单位）。
        返回时间值（整数），如果请求失败则抛出异常。
        """
        # 发送 get_time 请求，data 中包含维度名称
        resp = await self._client.request("get_time", {"level": self.name})
        if not resp.get("success"):
            error_msg = resp.get("error_message", "Unknown error")
            raise Exception(f"Failed to get time for level {self.name}: {error_msg}")
        # 成功响应中应包含 data.time
        time = resp["data"]["time"]
        return time

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Level('{self.name}')"

    def __eq__(self, other):
        if not isinstance(other, Level):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


# ----- 测试与示例代码 -----
async def main():
    from pycraft import PyModClient
    client = PyModClient()
    try:
        await client.connect()
        levels = await client.get_levels()
        print("Available levels:", [str(lvl) for lvl in levels])
        for level in levels:
            try:
                time = await level.get_time()
                print(f"Time in {level}: {time}")
            except Exception as e:
                print(f"Error getting time for {level}: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())