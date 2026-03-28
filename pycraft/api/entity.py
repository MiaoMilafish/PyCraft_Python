# pycraft/api/entity.py

from pycraft.api.level import Level
import asyncio


class Entity:
    """
    实体实例的引用
    """

    def __init__(self, client, level: Level, uuid: str, name: str):
        self._client = client
        self.level = level
        self.uuid = uuid
        self.name = name

    def __repr__(self):
        return f"<uuid={self.uuid} name={self.name}>"

    async def get_pos(self):
        resp = await self.level._client.request(
            "get_entity_pos",
            {
                "uuid": self.uuid
            }
        )
        if not resp.get("success"):
            raise Exception(resp.get("error_message"))
        data = resp.get("data")
        if not isinstance(data, dict):
            raise Exception(f"Invalid response data: {resp}")
        try:
            x = data["x"]
            y = data["y"]
            z = data["z"]
        except KeyError:
            raise Exception(f"Incomplete position data: {data}")
        result = (x, y, z)
        print("Debug:", result)
        return result


    async def teleport(self, x, y, z):
        """
        瞬移实体
        """
        resp = await self.level._client.request(
            "teleport_entity",
            {
                "uuid": self.uuid, 
                "x": x,
                "y": y,
                "z": z
            }
        )
        if not resp.get("success"):
            raise Exception(resp.get("error_message"))
        return True


    async def move_to(self, x, y, z, speed=0.2, eps=0.2):
        while True:
            px, py, pz = await self.get_pos()
            dx = x - px
            dz = z - pz
            dist = (dx * dx + dz * dz) ** 0.5
            if dist < eps:
                break
            await self.level._client.request("move_entity", {
                "uuid": self.uuid,
                "x": x,
                "y": y,
                "z": z,
                "speed": speed
            })
            await asyncio.sleep(0.05)  # ~1 tick
    
    async def set_perspective(self, mode: int = 0) -> bool:
        """
        切换玩家视角
        param mode: 0 - 第一人称, 1 - 第三人称背面, 2 - 第三人称正面
        return: 是否设置成功
        """
        if mode not in (0, 1, 2):
            raise ValueError(f"Invalid perspective mode: {mode}")
        # 发送请求到 Java 端
        resp = await self._client.request("set_perspective", {"mode": mode})
        if not resp.get("success"):
            raise Exception(resp.get("error_message"))
        return True

    async def set_rotation(self, yaw: float, pitch: float = 90.0):
        resp = await self._client.request("set_rotation", {"yaw": yaw, "pitch": pitch})
        if not resp.get("success"):
            raise Exception(resp.get("error_message"))
        return True
    
    async def get_rotation(self) -> tuple[float, float]:
        resp = await self._client.request("get_rotation", {})
        if not resp.get("success"):
            raise Exception(resp.get("error_message"))
        data = resp.get("data", {})
        return data["yaw"], data["pitch"]
    