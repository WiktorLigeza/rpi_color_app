#!bin/bash
pyinstaller main.py --onefile --hidden-import=websockets --hidden-import=websockets.legacy --hidden-import=websockets.legacy.client