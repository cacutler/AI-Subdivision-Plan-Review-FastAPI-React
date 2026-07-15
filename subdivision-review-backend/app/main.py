from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, plans, users

app = FastAPI(title="Subdivision Plan Review API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(plans.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}