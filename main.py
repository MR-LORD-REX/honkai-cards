from src.honkai_cards import HSR , Teammate
from src.honkai_cards.api import BuildAPI

from PIL import Image
import asyncio

team = [
    Teammate(
        characterId="1408",
        lightCone="23048",
        characterEidolon=0,
        lightConeSuperimposition=1,
    ),
    Teammate(
        characterId="1407",
        lightCone="23047",
        characterEidolon=0,
        lightConeSuperimposition=1,
    ),
    Teammate(
        characterId="1406",
        lightCone="23046",
        characterEidolon=0,
        lightConeSuperimposition=1,
    ),
]

uid=713987091

async def main():
    async with HSR() as hsr:
        c1=await hsr.profile(uid)
        c1.card.show()
        for c in c1.characters:
            print(c.name)
        c2=await hsr.character(uid,0)
        c2.show()
        c3=await hsr.custom_team(
            uid , teammates=team,
            slot=3
        )
        c3.save("test.png")

asyncio.run(main())