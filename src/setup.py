#!/usr/bin/env python3

# SUBTITLE-CORRECTOR IS LICENSED UNDER THE GNU GPLv3
# Copyright (C) 2023 Will Maguire

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

# The definition of Free Software is as follows:
# 	- The freedom to run the program, for any purpose.
# 	- The freedom to study how the program works, and adapt it to your needs.
# 	- The freedom to redistribute copies so you can help your neighbor.
# 	- The freedom to improve the program, and release your improvements
#   - to the public, so that the whole community benefits.

# A program is free software if users have all of these freedoms.

from setuptools import setup

# To create EXE for windows:
# pyinstaller.exe SRT-gui.py --onefile --hidden-import=tiktoken_ext.openai_public --hidden-import=tiktoken_ext

APP = ['SRT-gui.py']
DATA_FILES = []
options = {
    'packages': [
        'openai',
        'srt',
        'tiktoken',
        'cchardet',
        'chardet',
        'asyncio',
        'tkinter',
        'platform',
        'json'
    ],
    'iconfile': './icns/SRT-corrector.icns'
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': options},
    setup_requires=['py2app']
)
