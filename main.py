from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from auth import router as auth_router
from drive import router as drive_router
from routers import documents, spreadsheets, slides
import uvicorn
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(auth_router)
app.include_router(drive_router)
app.include_router(documents.router, prefix="/drive")
app.include_router(spreadsheets.router, prefix="/drive")
app.include_router(slides.router, prefix="/drive")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Google Drive Lister"}

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
