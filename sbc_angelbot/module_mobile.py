


import asyncio




class MobileRobot:
    def __init__(self, Q_sbc, name, addr) -> None:
        # 초기입력
        self.Q_sbc = Q_sbc
        self.name = name
        self.addr = addr
        # 후기입력
        self.reader = None
        self.writer = None
        self.status = {
            "status":"disconnect",
            "battery":0,
            "temperature":0,
            "location":{
                "x":0,
                "y":0,
                "theta":0
            }
        }
        # task
        self.task = {}

    async def connect(self):
        try:
            print(f"{self.name}에 접속 시동중...")
            self.reader, self.writer = await asyncio.open_connection(self.addr[0],self.addr[1])
            # omron arcl 접속 절차
            recv = await self.reader.read();        print(recv)
            self.writer.write(b"admin\r\n")
            await self.writer.drain()
            recv = await self.reader.read();        print(recv)
            print(f"{self.name} 에 접속 성공")
        except:
            self.reader = None
            self.writer = None
            print(f"{self.name}에 접속 실패")


    async def handle_recv(self):
        print(f"{self.name}에서 수신 대기 시작함")
        try:
            while True:
                recv = await self.reader.read()
                if not recv:
                    break
                await self.Q_sbc.put(recv);         print(recv)
        except:
            print(f"{self.name}에서 수신대기 중 오류 발생")
        finally:
            print(f"{self.name}의 수신 대기 정상종료")


    async def handle_send(self,msg):
        try:
            self.writer.write( msg.encode()+b"\r\n" )
            await self.writer.drain()
        except:
            print(f"{self.name}에서 msg 전달 실패")


if __name__=="__main__":
    print("프로그램이 시작됨")

    async def main():
        ro = MobileRobot( asyncio.Queue(),"robot",("192.168.215.219",7171) )

        ro.task["connect"] = asyncio.create_task( ro.connect() )
        print(ro.task)
        print()
        ro.task["handle_recv"] = asyncio.create_task( ro.handle_recv() )
        print(ro.task)


    loop = asyncio.get_event_loop()
    loop.create_task( main() )
    loop.run_forever()
    print("프로그램이 종료됨")
