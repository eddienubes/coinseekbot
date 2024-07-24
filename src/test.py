import asyncio


async def main():
    class SomeClass:
        def some_method(self):
            print(__name__)

    some_instance = SomeClass()
    some_instance.some_method()


asyncio.run(main())
