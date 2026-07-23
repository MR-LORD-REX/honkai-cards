from src.honkai_cards import HSR

from PIL import Image
import asyncio

uid=713987091

async def main():
    async with HSR() as hsr:
        c1=await hsr.profile(uid)
        c1.card.save("pfp.png")
        for c in c1.characters:
            print(c.name)
        c2=await hsr.character(uid,0)
        print(c2)
        c2.show()
    
asyncio.run(main())