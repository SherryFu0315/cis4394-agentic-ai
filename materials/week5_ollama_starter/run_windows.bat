@echo off
REM CIS 4394 Week 5 -- double-click me. No terminal knowledge needed.
setlocal enabledelayedexpansion
cd /d "%~dp0"
cls
echo ==================================================
echo  CIS 4394 . Week 5 -- tool-calling agent
echo  Folder: %CD%
echo ==================================================

set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo.
  echo Python 3 was not found on this PC.
  echo Install it from the Microsoft Store, then double-click this file again.
  echo.
  pause
  exit /b 1
)

%PY% -c "import ollama" >nul 2>&1
if errorlevel 1 (
  echo.
  echo Installing the 'ollama' Python package ^(one time, a few seconds^)...
  %PY% -m pip install --quiet ollama
  if errorlevel 1 (
    echo Install failed. Try running:  %PY% -m pip install ollama
    pause
    exit /b 1
  )
)

curl.exe -s --max-time 5 http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
  echo.
  echo !! Ollama does not seem to be running.
  echo    Open the Ollama app from the Start menu, then try again.
)

echo.
echo Type a question and press Enter. Press Enter alone for the invoice question.
echo Type  q  then Enter to quit.

:loop
echo.
set "Q="
set /p "Q=Question: "
if /I "!Q!"=="q" goto :end
echo --------------------------------------------------
if "!Q!"=="" (
  %PY% 1_agent_raw.py
) else (
  %PY% 1_agent_raw.py "!Q!"
)
echo --------------------------------------------------
goto :loop

:end
endlocal
