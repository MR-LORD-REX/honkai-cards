from __future__ import annotations

from pydantic import BaseModel

class Teammate(BaseModel):
    characterId: str
    lightCone:str
    characterEidolon:int =0
    lightConeSuperimposition: int =1
    
class Teammates(BaseModel):
    teammates:list[Teammate]