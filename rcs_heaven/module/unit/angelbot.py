from datetime import datetime
import asyncio
import json

from fastapi import WebSocket, FastAPI


class Manager:
    def __init__(self, name, addr, ws):
        self.name = name
        self.addr = addr
        self.ws = ws
        self.flag_idle_cobot = asyncio.Event(); self.flag_idle_cobot.set()
        self.flag_idle_mobot = asyncio.Event(); self.flag_idle_mobot.set()

        self.task = {}
        self.status = [
            self.flag_idle_cobot.is_set(),
            self.flag_idle_mobot.is_set(),
            {
                "status":"disconnect",
                "battery":0,
                "location":{
                    "x":0, "y":0, "theta":0
                },
                "temperature":0
            }
        ]
        

    async def handle_send(self, msg):
        try:
            await self.ws.send_text( msg )

        except Exception as e:
            print( self.name,"error handle_send",e )



    async def cobot_control(self, data):
        try:
            cmd = {
                "who":"rcs",
                "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                "where":"cobot",
                "what":"write",
                "how":data,
                "why":"request"
            }

            msg = json.dumps( cmd )
            await self.handle_send( msg )
            self.flag_idle_cobot.clear()

        except Exception as e:
            print( self.name,"error cobot_control",e )
                  


    async def mobot_control(self, data):
        try:

            cmd = {
                "who":"rcs",
                "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                "where":"mobot",
                "what":"write",
                "how":data,
                "why":"request"       
            }

            msg = json.dumps( cmd )
            await self.handle_send( msg )
            self.flag_idle_mobot.clear()

        except Exception as e:
            print( self.name,"error mobot_control",e )



