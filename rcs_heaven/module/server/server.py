import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from unit.angelbot import Manager as Angelbot

class Webserver:
    def __init__(self, NETWORK, UNITS, addr):
        self.NETWORK = NETWORK
        self.UNITS = UNITS
        self.addr = addr

        # 서버 설정
        self.app = FastAPI()
        # self.app.mount("/static", StaticFiles(directory="static"), name="static")

        # url 연결
        self.app.websocket("/unit_connect")(self.unit_connect)
        self.app.get("/", response_class=HTMLResponse)(self.showPage_landing)
        self.app.get("/manageUnit", response_class=HTMLResponse)(self.showPage_manageUnit)
        self.app.post("/test", response_class=HTMLResponse)(self.pb_test)
        # self.app.post("/pb_dbCreate")(self.registeUnit)
        # self.app.get("/dbRead")(self.dbRead)


    async def run(self):
        print("서버모듈 기동함")
        server = uvicorn.Server( uvicorn.Config( self.app, self.addr[0], self.addr[1] ) )
        await server.serve()
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
                msg = await ws.receive()
                print(msg)

            except Exception as e:
                print(name, "error 연결 끊김", e)
                try:
                    await ws.close()
                except:
                    print("웹소켓 닫기시도 실패.")
                finally:
                    break

        print(name, "연결 종료")


    async def pb_test(self, request: Request):
        await self.UNITS["unit_220"].ws.send_text("버튼으로 동작함")
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
