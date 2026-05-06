@echo off
setlocal
cd /d "%~dp0"
python worker\dispatch_worker.py
