from datetime import datetime
import asyncio
import json
from datetime import datetime

from fastapi import WebSocket, FastAPI


class Manager:
    def __init__(self, UNITS, name, addr, ws):
        self.UNITS = UNITS
        self.name = name
        self.addr = addr
        self.ws = ws
        self.task = {}

        self.flag_idle = asyncio.Event(); self.flag_idle.set(); self.flag_idle_on=True
        # print(self.name,"이벤트 플래그 True 됨")
        self.work=[]
        self.work_n = 0
        self.status = {
            "work":[],
            "work_n":0
        }

        self.task["work_controller"] = asyncio.get_running_loop().create_task( self.work_controller() )


    # async def updateStatus(self,status):
    #     try:
    #         self.status = status
    #     except Exception as e:
    #         print(self.name,"error updateStatus",e)
        

    async def work_controller(self):
        await asyncio.sleep(4)

        while True:
            try:
                msg = self.work[self.work_n]
                print("작업리스트에서 작업 꺼내옴!")
                print(msg)

            except IndexError:
                print(self.name, "작업리스트가 비었거나 끝남!")
                self.work=[]
                self.work_n = 0
                await asyncio.sleep(2)
                continue

            except Exception as e:
                print(self.name,"Error work_controller\n",e)
                await asyncio.sleep(2)
                continue

            ###################################################################
            try:
                await asyncio.sleep(2)
                await self.flag_idle.wait()
                # await asyncio.sleep(2)
                # await self.flag_idle.wait()
                print("행동시작")
                
                ###################################################################

                if msg["what"] == "wait":
                    await asyncio.sleep(2)
                    await self.UNITS[msg["how"]].flag_idle.wait()
                    # await asyncio.sleep(2)
                    # await self.UNITS[msg["how"]].flag_idle.wait()
                    # await asyncio.sleep(2)
                    # await self.UNITS[msg["how"]].flag_idle.wait()
                

                    # print(f"{self.UNITS[msg['how']]}의 플래그 True 됨~~~~~~~~~~~~~~~~~~~~~~~")
                    # print(self.UNITS[msg["how"]].flag_idle.is_set())

                elif msg["what"] == "time":
                    # print( msg["how"] )
                    # print(self.name,datetime.now())
                    now = datetime.now()
                    time_obj = datetime.strptime(msg["how"], "%H:%M:%S").time()

                    # 오늘 날짜와 문자열에서 생성한 시간 객체를 결합합니다.
                    combined_time = datetime.combine(now.date(), time_obj)

                    # 시간 차이를 계산합니다.
                    time_difference = combined_time - now

                    # 결과를 초 단위로 출력하려면 total_seconds()를 사용합니다.
                    seconds_difference = time_difference.total_seconds()

                    if seconds_difference >= 0:
                        print(self.name, seconds_difference, "만큼 대기 중")
                        await asyncio.sleep(seconds_difference)
                    else:
                        print("시간차가 음수임!")



                else:
                    await self.handle_send( msg )
                    # print("!!!!!!!!!!!!!!!")
            
            except Exception as e:
                print(self.name,"error work_controller\n",e)

            finally:
                # await asyncio.sleep(4)
                # await self.flag_idle.wait()
                await asyncio.sleep(2)
                await self.flag_idle.wait()

                print("플래그 idle 됨!")
                self.work_n += 1


    async def handle_send(self, msg):
        print("?????????????????")
        try:
            await self.ws.send_text( json.dumps(msg) )
            print("전송함")

        except Exception as e:
            print( self.name,"error handle_send",e )



    # async def cobot_control(self, data):
    #     try:
    #         cmd = {
    #             "who":"rcs",
    #             "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
    #             "where":"cobot",
    #             "what":"write",
    #             "how":data,
    #             "why":"request"
    #         }

    #         msg = json.dumps( cmd )
    #         await self.handle_send( msg )
    #         self.flag_idle_cobot.clear()

    #     except Exception as e:
    #         print( self.name,"error cobot_control",e )
                  


    # async def mobot_control(self, data):
    #     try:

    #         cmd = {
    #             "who":"rcs",
    #             "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
    #             "where":"mobot",
    #             "what":"write",
    #             "how":data,
    #             "why":"request"       
    #         }

    #         msg = json.dumps( cmd )
    #         await self.handle_send( msg )
    #         self.flag_idle_mobot.clear()

    #     except Exception as e:
    #         print( self.name,"error mobot_control",e )



