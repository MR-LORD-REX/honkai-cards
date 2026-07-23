"""Generate a character showcase card with DPS benchmark."""

import asyncio

from honkai_cards import HSR

UID = 713987091  # replace with your in-game UID


async def main() -> None:
    async with HSR() as hsr:
        # slot: 0–7 (character position in the showcase)
        # benchmark: include DPS benchmark on the card
        card = await hsr.character(UID, slot=0, benchmark=True)

        if card is None:
            print("No character found for this slot.")
            return

        card.save("character_card.png")
        print("Saved character_card.png")
        card.show()


if __name__ == "__main__":
    asyncio.run(main())
