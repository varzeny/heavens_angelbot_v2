
import asyncio
import websockets
import json
from datetime import datetime # datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" )

from neuromeka_indy7.controller import Controller


class UnitCoffee:
    def __init__(self, name, addr_rcs:list, parts:list) -> None:
        self.name = name
        self.addr_rcs = addr_rcs
        
        self.rcs = None
        self.Q_msg = asyncio.Queue()
        self.flag_idle = asyncio.Event(); self.flag_idle.set()
        self.parts = {}
        for nip in parts:
            self.parts[nip[0]] = Controller([nip[1],nip[2]])
        self.status={
            "flag_idle":self.flag_idle.is_set(),
            "parts":[],
            "location":{
                "x":9600,
                "y":2200,
                "theta":0
                }
        }

        self.loop = asyncio.get_event_loop()

    def run(self):
        try:
            print(self.name,"called")
            self.loop.create_task(self.main())
            self.loop.run_forever()
        except Exception as e:
            print(self.name, "error run\n",e)
        finally:
            print(self.name,"return run")

    async def main(self):
        print(self.name,"called main")
        
        for p in self.parts:
            self.loop.create_task(self.parts[p].run())
            self.loop.create_task(self.updateStatus())

        print("parts 연결완료")

        while True:
            await asyncio.sleep(1)
            try:
                self.rcs = await websockets.connect(
                    f"ws://{self.addr_rcs[0]}:{self.addr_rcs[1]}/unit_connect"
                )
                await self.rcs.send(f"{self.name}")
                print(self.name,"rcs 접속 성공")
                
            except Exception as e:
                print(self.name,"error rcs 접속 오류 재시도 중...\n",e)
                continue


            try:
                print(self.name,"rcs 의 명령 대기중...")
                async for recv in self.rcs:
                    try:
                        msg = json.loads(recv)
                    except Exception as e:
                        print("메세지 json 변환 오류")
                        continue
                    print(msg)
                    self.loop.create_task(self.checkMsg(msg))

            except Exception as e:
                print(self.name,"rcs 명령 수신 대기중에 오류 발생\n",e)
                continue


    async def updateStatus(self):
        await asyncio.sleep(4)
        while True:
            self.status["flag_idle"] = self.flag_idle.is_set()
            self.status["parts"] = [self.parts[p].status for p in self.parts]
            self.status["location"] = {"x":9600,"y":2200,"theta":0}

            try:
                data = {
                    "why":"update",
                    "who":self.name,
                    "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                    "where":"rcs",
                    "what":"status",
                    "how":self.status
                }
                msg = json.dumps(data)
                # print(msg)
                await self.rcs.send(msg)

            except Exception as e:
                print(self.name,"rcs로 스테이터스 전송 오류\n",e)
                
            finally:
                await asyncio.sleep(1)

    async def checkMsg(self,msg):
        if msg["what"] == "make":
            if msg["how"] == "coffee":
                # 작업시작
                self.flag_idle.clear()

                await self.parts["neuromeka_1"].flag_idle.wait()
                await self.parts["neuromeka_2"].flag_idle.wait()

                await self.parts["neuromeka_1"].reg_write(11,[1])
                await self.parts["neuromeka_2"].reg_write(11,[1])

                await self.parts["neuromeka_1"].reg_write(1,[1])
                await self.parts["neuromeka_2"].reg_write(1,[1])

                ################
                await asyncio.sleep(2)

                while True:
                    rgs = await self.parts["neuromeka_1"].reg_read(0,1)
                    complet =rgs[0]
                    print("뉴로메카1의 레지0 = ",complet)
                    if complet == 0:
                        break
                    await asyncio.sleep(1)
                
                await self.parts["neuromeka_2"].reg_write(2,[1])

                ##################
                await asyncio.sleep(2)

                while True:
                    rgs=await self.parts["neuromeka_2"].reg_read(0,1)
                    complet = rgs[0]
                    if complet == 0:
                        break
                    await asyncio.sleep(1)

                print("커피 작업 완료!!!!!!!")
                self.flag_idle.set()


if __name__=="__main__":

    print( "unit 프로그램이 시작" )
    unit = UnitCoffee(
        name="unit_coffee",
        addr_rcs=["192.168.212.189",8000],
        parts=[
            ("neuromeka_1","192.168.215.124",502),
            ("neuromeka_2","192.168.215.123",502),
        ]
    )
    unit.run()
    print( "unit 프로그램이 종료" )
