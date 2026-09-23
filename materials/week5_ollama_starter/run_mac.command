#!/bin/bash
# CIS 4394 Week 5 — double-click me. No terminal knowledge needed.
cd "$(dirname "$0")" || exit 1
clear
echo "=================================================="
echo " CIS 4394 · Week 5 — tool-calling agent"
echo " Folder: $(pwd)"
echo "=================================================="

if [ -x "./venv/bin/python" ]; then PY="./venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then PY="python3"
else
  echo; echo "Python 3 was not found on this Mac."
  echo "Install it from python.org, then double-click this file again."
  echo; read -r -p "Press Enter to close."; exit 1
fi

if ! "$PY" -c "import ollama" >/dev/null 2>&1; then
  echo; echo "Installing the 'ollama' Python package (one time, a few seconds)..."
  "$PY" -m pip install --quiet ollama || {
    echo "Install failed. Try:  $PY -m pip install ollama"; read -r -p "Press Enter to close."; exit 1; }
fi

if ! curl -s --max-time 5 http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo; echo "!! Ollama does not seem to be running."
  echo "   Open the Ollama app (Launchpad), wait for the icon, then try again."
fi

echo
echo "Type a question and press Enter. Press Enter alone for the invoice question."
echo "Type  q  then Enter to quit."
while true; do
  echo; printf "Question: "; IFS= read -r Q
  [ "$Q" = "q" ] && break
  echo "--------------------------------------------------"
  if [ -z "$Q" ]; then "$PY" 1_agent_raw.py; else "$PY" 1_agent_raw.py "$Q"; fi
  echo "--------------------------------------------------"
done
