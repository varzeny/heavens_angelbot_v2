
import asyncio
from fastapi import WebSocket, FastAPI

class Manager:
    def __init__(self, name, addr, ws):
        self.name = name
        self.addr = addr
        self.ws = ws
        self.work = "idle"
        self.task = {}
        self.status = {
            "battery":0,
            "location":{
                "x":0, "y":0, "theta":0
            },
            "tcp":{
                "x":0, "y":0, "z":0, "rx":0, "ry":0, "rz":0
            }
        }

