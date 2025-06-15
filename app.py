# app.py
from fastapi import FastAPI, HTTPException
from main import InstagramAnalyzer
import argparse
import asyncio

app = FastAPI()

@app.get("/analyze/{username}")
async def analyze(username: str, limit: int = 7):
    analyzer = InstagramAnalyzer()
    try:
        # Запускаем синхронный метод в потоке
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, analyzer.process_username, username, limit)
        return {"status": "done"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
