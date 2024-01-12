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

import subtitlecorrector as stc
from subtitlecorrector import Config
import prompts as prompts
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import platform
import os

# Note: This GUI code was hacked together in a day, Thusly it is incredibly messy. 
#       If thou endeavourest to clean it up, then I hope that the spirit of programming walketh with thee. 

class SRTCorrectorGui:
    # Process file.
    def process_subtitle(self):
        if (self.full_output_path != "" and self.subtitle_file_path != ""):
            self.sfile_status_label.config(text="Processing started...")
            stc.correct_subtitles(self.subtitle_file_path, self.prompt_dict[self.selected_prompt.get()], self.full_output_path)
            self.sfile_status_label.config(text="Processing completed.")
        else:
            self.sfile_status_label.config(text="Please select the path to the input subtitle and the path for the output.")

    # Select prompt.
    def prompt_selected(self, *args):
        if (self.selected_prompt.get() != 0):
            self.sfile_button.config(state="normal")

    # Select file.
    def choose_file(self):
        self.subtitle_file_path = filedialog.askopenfilename()
        if self.subtitle_file_path:
            self.path_entry.config(state="normal")
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.subtitle_file_path)
            self.path_entry.config(state="readonly")
            self.ofile_button.config(state="normal")

    def choose_odir(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            self.full_output_path = self.output_dir + "/" + "corrected_" + os.path.basename(self.subtitle_file_path)
            self.ofile_path.config(state="normal")
            self.ofile_path.delete(0, tk.END)
            self.ofile_path.insert(0, self.full_output_path)
            self.ofile_path.config(state="readonly")
            open(self.full_output_path, "w+")
            self.sfile_process_button.config(state="normal", text="Process subtitle file")

    # Sets up the GUI for selecting a file.
    def file_selection_GUI(self):
        self.file_frame = tk.Frame(master=self.root_window, width=100, height=100)
        self.sfile_path_label = tk.Label(master=self.file_frame, text="Subtitle file: ")
        self.path_entry = tk.Entry(master=self.file_frame, width=40, state="readonly")
        self.sfile_button = tk.Button(
            master=self.file_frame,
            text="Select...",
            command=self.choose_file,
            state=tk.DISABLED
        )
        self.path_entry.config(readonlybackground=self.path_entry.cget("background"))
        self.file_frame.pack(fill=tk.X)
        self.sfile_path_label.pack(padx=10, side="left")
        self.path_entry.pack(padx=10, side="left")
        self.sfile_button.pack(padx=10, side="left")
        
    # Output file selection component.
    def ofile_selection_GUI(self):
        self.outputfile_frame = tk.Frame(master=self.root_window, width=100, height=100)
        self.ofile_label = tk.Label(master=self.outputfile_frame, text="Output folder:")
        self.ofile_path = tk.Entry(master=self.outputfile_frame, width=40, state="readonly")
        self.ofile_button = tk.Button(
            master=self.outputfile_frame,
            text="Select...",
            command=self.choose_odir,
            state=tk.DISABLED
        )
        self.ofile_path.config(readonlybackground=self.ofile_path.cget("background"))
        self.outputfile_frame.pack(fill=tk.X)
        self.ofile_label.pack(padx=5, side="left")
        self.ofile_path.pack(padx=10, side="left")
        self.ofile_button.pack(padx=10, side="left")

    # Sets up the GUI for processing a file.
    def processing_GUI(self):
        self.sfile_status_label = tk.Label(
            master=self.root_window,
            text="Status: processing not started",
        )
        self.sfile_process_button = tk.Button(
            master=self.root_window,
            text="No file yet selected",
            command=self.process_subtitle,
            state=tk.DISABLED
        )
        self.sfile_status_label.pack()
        self.sfile_process_button.pack()

    # Constructor
    def __init__(self):
        # Variables:
        self.subtitle_file_path = ""
        self.full_output_path = ""
        self.output_dir = ""
        self.config = Config()
        self.prompts = prompts.load_prompts_from_directory(self.config.prompt_directory)
        self.prompt_dict = {}
        for prompt in self.prompts:
            self.prompt_dict.update({prompt.name: prompt})
        
        # Window initialisation:
        self.root_window = tk.Tk()
        self.root_window.title = "Subtitle Corrector GUI"
        self.root_window.geometry("425x150")

        # Prompt Selection:
        self.selected_prompt = StringVar(self.root_window)
        self.selected_prompt.set("Select prompt...")
        self.prompt_select = OptionMenu(self.root_window, self.selected_prompt, *self.prompt_dict, command=self.prompt_selected)
        self.prompt_select.pack()

        # General setup:
        self.file_selection_GUI()
        self.ofile_selection_GUI()
        self.processing_GUI()
        self.license_label = tk.Label(self.root_window, text="Subtitle Corrector is Free Software licensed under the GNU GPLv3")
        self.license_label.pack(side="bottom")

def main():
    SRT_corrector = SRTCorrectorGui()
    SRT_corrector.root_window.mainloop()

main()
