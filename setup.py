#!/usr/bin/env python3

from setuptools import setup

# To create EXE for windows:
# .\SRT-gui.py --onefile --hidden-import=tiktoken_ext.openai_public --hidden-import=tiktoken_ext --windowed

APP = ['SRT-gui.py']
DATA_FILES = []
options = {
    'packages': [
        'openai',
        'srt',
        'tiktoken',
        'cchardet',
        'chardet'
    ],
    'iconfile': './icns/SRT-corrector.icns'
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': options},
    setup_requires=['py2app']
)
