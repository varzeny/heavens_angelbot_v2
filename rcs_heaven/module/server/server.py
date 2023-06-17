import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from unit.angelbot import Manager as Angelbot

import json
from datetime import datetime    # datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" )


class Webserver:
    def __init__(self, NETWORK, UNITS, addr):
        self.NETWORK = NETWORK
        self.UNITS = UNITS
        self.addr = addr

        # 서버 설정
        self.app = FastAPI()
        self.app.mount("/static", StaticFiles(directory="./module/server/static"), name="static")

        # url 연결
        self.app.post("/reqWork")(self.reqWork)
        self.app.websocket("/unit_connect")(self.unit_connect)
        self.app.get("/", response_class=HTMLResponse)(self.showPage_landing)
        self.app.get("/manageUnit", response_class=HTMLResponse)(self.showPage_manageUnit)
        self.app.post("/test", response_class=HTMLResponse)(self.pb_test)
        self.app.post("/send2unit", response_class=HTMLResponse)(self.send2unit)
        # self.app.post("/pb_dbCreate")(self.registeUnit)
        # self.app.get("/dbRead")(self.dbRead)


    async def run(self):
        print("서버모듈 기동함")

        try:
            server = uvicorn.Server( uvicorn.Config( self.app, self.addr[0], self.addr[1] ) )
            await server.serve()

        except Exception as e:
            print("error 서버모듈",e)

        print("서버모듈 종료됨")


    async def unit_connect(self, ws: WebSocket):
        try:
            await ws.accept()
            name = await ws.receive_text()
            addr = ws.client.host
            self.UNITS[name] = Angelbot(name, addr, ws)
            print(self.UNITS)

        except Exception as e:
            print("접속 과정 중 오류", e)

        while True:
            try:
                recv = await ws.receive_text()
                print(recv)

            except WebSocketDisconnect:
                print(name,"연결이 종료됨")
                break

            except Exception as e:
                print(name,"데이터 수신중 오류",e)
                continue

            try:
                msg = json.loads( recv )
                if msg["why"] == "update":
                    self.UNITS[name].status = msg["how"]
                    if msg["how"][0]:
                        self.UNITS[name].flag_idle_cobot.set()
                    if msg["how"][1]:
                        self.UNITS[name].flag_idle_mobot.set()
                    continue

                await self.NETWORK.put( msg )

            except Exception as e:
                print(name,"error 데이터 변환 혹은 큐에 넣기",e)
                continue


    async def reqWork(self, request: Request):
        data = await request.json()

        msg = {
            "who":"front",
            "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
            "where":"logic",
            "what":"work",
            "how":data,
            "why":"request"
        }
        await self.NETWORK.put( msg )


        return {"data":"success"}


    async def send2unit(self, request: Request):
        print("***************")
        msg = await request.json()
        print(msg)
        await self.UNITS["unit_219"].handle_send( json.dumps(msg) )


    async def pb_test(self, request: Request):
        await self.UNITS["unit_219"].handle_send("버튼으로 동작함")
        print("&&&&&")


    async def showPage_landing(self):
        return FileResponse("./module/server/page/landing.html")


    async def showPage_manageUnit(self):
        return FileResponse("./module/server/page/manageUnit.html")

    # async def registeUnit(self, request: Request):
    #     data = await request.json()
    #     print(data)

    #     newUnit = Angelbot(
    #         type=data['type'],
    #         name=data['name'],
    #         ip=data['ip'],
    #         port=data['port'],
    #         active=False,
    #         status=None,
    #         battery=None,
    #         x=None,
    #         y=None,
    #         z=None
    #     )
    #     async with async_session() as session:
    #         session.add(newUnit)
    #         await session.commit()

    #     print("db 등록 완료")
    #     return {"message": "Angelbot registered successfully"}

    # async def dbRead(self):
    #     async with async_session() as session:
    #         result = await session.execute(select(Angelbot))
    #         units = result.scalars().all()
    #         return units


if __name__ == "__main__":
    network = None  # Provide your network object
    units = {}  # Provide your units object
    addr = ("127.0.0.1",8000)  # Provide your address
    server = Webserver(network, units, addr)
    server.run()
