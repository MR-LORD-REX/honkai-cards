"""Generate a player profile card and list showcase characters."""

import asyncio

from honkai_cards import HSR

UID = 713987091  # replace with your in-game UID


async def main() -> None:
    async with HSR() as hsr:
        profile = await hsr.profile(UID)

        profile.card.save("profile_card.png")
        print("Saved profile_card.png")
        print("Showcase characters:", profile.characters)
        # Each entry has .slot and .charid
        for char in profile.characters:
            print(f"  slot {char.slot}: character id {char.charid}")


if __name__ == "__main__":
    asyncio.run(main())
