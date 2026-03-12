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