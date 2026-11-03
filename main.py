from app.routers import issues
from fastapi import FastAPI
from app.routers import users
from app.database import engine, Base
from app import models
from app.routers import comments
from app.routers import projects
from app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Issue Tracker API",
    description="API for managing projects, issues and comments",
    version="1.0.0"
)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(issues.router)
app.include_router(comments.router)






@app.get("/")
def root():
    return {
        "message": "Welcome to Issue Tracker API"
    }
