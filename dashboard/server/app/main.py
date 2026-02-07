from fastapi import FastAPI

app = FastAPI(title="My Awesome API")


@app.get("/")
def read_root():
    return {"message": "Welcome to your FastAPI backend!"}


@app.get("/health")
def get_health():
    return {"status": 200}
