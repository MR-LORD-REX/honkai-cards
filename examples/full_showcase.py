"""Fetch a profile card and every character card in the showcase."""

import asyncio

from honkai_cards import HSR

UID = 713987091  # replace with your in-game UID


async def main() -> None:
    async with HSR() as hsr:
        profile = await hsr.profile(UID)
        profile.card.save("profile_card.png")
        print(f"Profile saved · {len(profile.characters)} characters in showcase")

        for char in profile.characters:
            card = await hsr.character(UID, slot=char.slot, benchmark=True)
            if card is None:
                print(f"  slot {char.slot}: skipped (no data)")
                continue

            path = f"character_slot_{char.slot}.png"
            card.save(path)
            print(f"  slot {char.slot} (id {char.charid}): saved {path}")


if __name__ == "__main__":
    asyncio.run(main())
