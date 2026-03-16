# pycraft/api/entity.py

from pycraft.api.level import Level


class Entity:
    """
    实体实例的引用
    """

    def __init__(self, client, level: Level, entity_id: int, name: str):
        self._client = client
        self.level = level
        self.entity_id = entity_id
        self.name = name

    def __repr__(self):
        return f"<Entity id={self.entity_id} name={self.name}>"

    async def get_pos(self):
        """
        获取实体位置
        """
        resp = await self._client.request(
            "get_entity_pos",
            {
                "entity_id": self.entity_id
            }
        )

        if not resp.get("success"):
            raise Exception(resp.get("error_message"))

        data = resp["data"]

        return (
            data["x"],
            data["y"],
            data["z"]
        )


    async def teleport(self, x, y, z):
        """
        瞬移实体
        """
        resp = await self._client.request(
            "teleport_entity",
            {
                "entity_id": self.entity_id,
                "x": x,
                "y": y,
                "z": z
            }
        )

        if not resp.get("success"):
            raise Exception(resp.get("error_message"))


    async def move_to(self, x, y, z, speed=0.2):
        """
        让实体以一定速度移动到目标位置
        """
        resp = await self._client.request(
            "move_entity",
            {
                "entity_id": self.entity_id,
                "x": x,
                "y": y,
                "z": z,
                "speed": speed
            }
        )
        if not resp.get("success"):
            raise Exception(resp.get("error_message"))