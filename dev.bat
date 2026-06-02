@echo off
SETLOCAL

set "PROJECT_DIR=%~dp0"

where wt >nul 2>nul
if %ERRORLEVEL% equ 0 (
    wt -d "%PROJECT_DIR%backend" cmd /k "call .newcitenv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000" ; split-pane -H -d "%PROJECT_DIR%frontend" cmd /k "npm run dev"
) else (
    echo [dev] Windows Terminal not found, opening separate windows...
    start "NewCitizen Backend" cmd /k "cd /d %PROJECT_DIR%backend && call .newcitenv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    start "NewCitizen Frontend" cmd /k "cd /d %PROJECT_DIR%frontend && npm run dev"
)
