import asyncio

import pyrogram

api_id = input("Введите api_id: ")
api_hash = input("Введите api_hash: ")


async def main():
    async with pyrogram.Client(api_id=api_id, api_hash=api_hash, name="name") as client:
        print(await client.export_session_string())


if __name__ == "__main__":
    asyncio.run(main())
