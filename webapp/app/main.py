from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return{"Hello": "World"}

@app.get("/test1")
async def read_root():
    return{"Hello": "World1"}