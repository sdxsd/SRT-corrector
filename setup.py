#!/usr/bin/env python3

from setuptools import setup

# To create EXE for windows run "pyinstaller .\SRT-gui.py --windowed --onefile"

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
