import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
##############################################################



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")




@app.get("/", response_class=HTMLResponse)
async def showPage_landing():
    return FileResponse("page/landing.html")


@app.get("/manageUnit", response_class=HTMLResponse)
async def showPage_manageUnit():
    return FileResponse("page/manageUnit.html")


@app.post("/pb_registering")
async def registeUnit(request:Request):
    data = await request.json()
    print(data)




##############################################################
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
