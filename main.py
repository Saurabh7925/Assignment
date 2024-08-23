from fastapi import FastAPI, Request, Depends, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import models
from db import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import traceback
from time import perf_counter
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="assignment")


models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.middleware("http")
async def profiler(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(perf_counter() - start)
    return response


@app.post("/save-item")
async def save_item(
    title: str = Form(...),
    description: str = Form(...),
    quantity: int = Form(...),
    price: int = Form(...),
    date: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        item_data = {
            "title": title,
            "description": description,
            "quantity": quantity,
            "price": price,
            "date": datetime.strptime(date, "%Y-%m-%d"),
            "image": await image.read() if image else None
        }

        item = models.Item(**item_data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return {"success": True}
    except Exception as e:
        print("Error:", e)
        print("Traceback:", traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/get-items")
def get_items(title: str = '', startDate: str = '', endDate: str = '', page: int = 1, db: Session = Depends(get_db)):
    try:
        print(f"Received request with title: {title}, startDate: {startDate}, endDate: {endDate}, page: {page}")
        query = db.query(models.Item)
        if title:
            query = query.filter(models.Item.title.like(f"%{title}%"))
        if startDate:
            query = query.filter(models.Item.date >= startDate)
        if endDate:
            query = query.filter(models.Item.date <= endDate)
        items = query.offset((page - 1) * 10).limit(10).all()
        total = db.query(models.Item).count()
        return {"items": [item.to_dict() for item in items], "total": total}
    except Exception as e:
        print("Error:", e)
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
