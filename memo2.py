import asyncio


async def A():
    print("a 시작됨")
    asyncio.create_task( B() )
    print("a 종료됨")

async def B():
    print("b 시작됨")

    print("b 종료됨")

async def main():
    print("main 시작됨")
    asyncio.create_task( A() )

    while True:
        print( asyncio.all_tasks() )
        await asyncio.sleep(0.01)
        
    print("main 종료됨")

loop = asyncio.get_event_loop()
loop.create_task( main() )
loop.run_forever()
