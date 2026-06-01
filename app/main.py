from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import auth, analyze
from app.db.database import engine, Base
import os
import sys

# Criar tabelas do banco
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Phishing & AI Content Detection API")

# Compatibilidade com PyInstaller
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminhos para arquivos estáticos e templates
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates HTML
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Rotas
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/dashboard")
async def read_dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time

    def open_browser():
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:8000")

    threading.Thread(target=open_browser).start()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_config=None
    )
