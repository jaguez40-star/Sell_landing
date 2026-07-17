@echo off
cd /d "%~dp0"
echo Iniciando API FastAPI en http://localhost:8890 ...
uv run uvicorn app.main:app --reload --port 8890
pause
