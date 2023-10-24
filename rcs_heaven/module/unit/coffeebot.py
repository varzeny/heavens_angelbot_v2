import asyncio
from datetime import datetime
import json

class Manager:
    def __init__(self, UNITS, name, addr, ws):
        self.UNITS = UNITS
        self.name = name
        self.addr = addr
        self.ws = ws

        self.work=[]
        self.work_n = 0
        self.flag_idle = asyncio.Event(); self.flag_idle.set(); self.flag_idle_on=True
        self.status = {}
        self.task = {}

        self.task["work_controller"] = asyncio.get_running_loop().create_task( self.work_controller() )


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
                await asyncio.sleep(2)
                await self.flag_idle.wait()
                
                ###################################################################

                await self.handle_send( msg )
                print("!!!!!!!!!!!!!!!")
            
            except Exception as e:
                print(self.name,"error work_controller\n",e)

            finally:
                await asyncio.sleep(2)
                await self.flag_idle.wait()
                await asyncio.sleep(2)
                await self.flag_idle.wait()
                print("플래그 idle 됨!")
                self.work_n += 1



    async def handle_send(self, msg):
        try:
            await self.ws.send_text( json.dumps(msg) )

        except Exception as e:
            print( self.name,"error handle_send",e )




    # async def coffee_control(self):
    #     try:
    #         self.flag_idle.clear()

    #         cmd = {
    #             "who":"rcs",
    #             "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
    #             "where":"coffee",
    #             "what":"write",
    #             "how":True,
    #             "why":"request"
    #         }

    #         msg = json.dumps( cmd )
    #         await self.handle_send( msg )
    #         self.flag_idle.clear()
    #         await asyncio.sleep(1)
    #         self.flag_idle.set()

    #     except Exception as e:
    #         print( self.name,"error coffee_control",e )
