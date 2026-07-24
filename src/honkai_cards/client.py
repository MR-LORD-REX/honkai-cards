from PIL import Image

from .api import BuildAPI
from .characters.character1 import build_character1
from .profile.profile1 import build_profile1

from .models.profile import P1Char , Profile1
from .models.customTeams import Teammates , Teammate

class HSR:
    def __init__(self) -> None:
        self.api=BuildAPI()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        pass
    
    async def character(
        self,
        uid:int|str,
        slot:int=0,
        benchmark:bool=True
    )-> Image.Image | None:
        """
        get character showcase 
        
        args:
        uid = 80000000 (in game uid)
        slot = 0 ( 0-7  character from showcase )
        benchmark= True|False (run character dps benchmark)
        
        """
        data=await self.api.get_build(uid,slot,benchmark=benchmark)
        
        return await build_character1(data)
    
    async def custom_team(
        self,
        uid:int|str,
        teammates: list[Teammate],
        slot:int=0,
        benchmark:bool=True
    )-> Image.Image | None:
        """
        get character showcase 
        
        args:
        uid = 80000000 (in game uid)
        slot = 0 ( 0-7  character from showcase )
        benchmark= True|False (run character dps benchmark)
        
        
        """
        data=await self.api.get_custom_build(uid,slot,benchmark=benchmark,team=teammates)
        
        return await build_character1(data)
    
    async def profile(
        self,
        uid: int|str
    )-> Profile1:
        """
        get profile card
        
        args:
        uid=8000000 ( in game uid )
        """
        
        data=await self.api.get_profile(uid)
        card = await build_profile1(data)
        chars=[]
        for i, c in enumerate(data.characters):
            chars.append(
                P1Char(
                    slot=i,
                    charid=c.id,
                    name=c.name
                )
            )
        pfp=Profile1(
            characters=chars,
            card=card
        )
        return pfp