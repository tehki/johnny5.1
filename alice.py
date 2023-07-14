import asyncio
import nest_asyncio
nest_asyncio.apply()

async def my_coroutine():
    return

async def main():
    # Create and gather your coroutines here
    coroutines = [my_coroutine()]
    await asyncio.gather(*coroutines)

if __name__ == "__main__":
    asyncio.run(main())