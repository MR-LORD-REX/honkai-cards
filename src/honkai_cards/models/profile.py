from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from PIL import Image

class Icons(BaseModel):
    character_id: str
    round: str
    gacha: str
    card: str

class Character(BaseModel):
    id: int
    icons: Icons
    eidolon: int
    name: str
    lvl: int
    rarity: int
    path: str
    element: str


class PlayerStats(BaseModel):
    achievement_count: int
    light_cone_count: int
    character_count: int
    max_simulated_universe_world: int
    book_count: int
    relic_count: int
    music_count: int


class Player(BaseModel):
    nickname: str
    signature: str
    uid: int
    level: int
    equilibrium_level: int
    friend_count: int
    stats: PlayerStats
    icon: str

class Profile(BaseModel):
    characters: list[Character]
    player: Player
    
class P1Char(BaseModel):
    slot:int
    charid:int
    
class Profile1(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    
    card:Image.Image
    characters:list[P1Char]