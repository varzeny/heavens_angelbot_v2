import asyncio
from datetime import datetime
import json

class Manager:
    def __init__(self, name, addr, ws):
        self.name = name
        self.addr = addr
        self.ws = ws
        self.flag_idle_coffee = asyncio.Event(); self.flag_idle_coffee.set()
        self.status = [
            self.flag_idle_coffee.is_set(),
            True,
            {
                "status":"connect",
                "battery":0,
                "location":{
                    "x":9600, "y":2200, "theta":0
                },
                "temperature":0
            }
        ]


    async def coffee_control(self):
        try:
            self.flag_idle_coffee.clear()

            cmd = {
                "who":"rcs",
                "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                "where":"coffee",
                "what":"write",
                "how":True,
                "why":"request"
            }

            msg = json.dumps( cmd )
            await self.handle_send( msg )
            self.flag_idle_coffee.clear()
            await asyncio.sleep(1)
            self.flag_idle_coffee.set()

        except Exception as e:
            print( self.name,"error coffee_control",e )



    async def handle_send(self, msg):
        try:
            await self.ws.send_text( msg )

        except Exception as e:
            print( self.name,"error handle_send",e )