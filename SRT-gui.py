#!/usr/bin/env python3

import subtitlecorrector as st
import tkinter as tk
from tkinter import filedialog

class SRTCorrectorGui:
    # Atrributes:
    subtitle_file_path = ""

    # Methods:
    def process_subtitle(self):
        self.sfile_status_label.config(text="Processing started...")
    def choose_file(self):
        subtitle_file_path = filedialog.askopenfilename()
        if subtitle_file_path:
            self.path_entry.config(state="normal")
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, subtitle_file_path)
            self.path_entry.config(state="readonly")
            self.sfile_process_button.config(state="normal", text="Process subtitle file")
    # Constructor
    def __init__(self):
        # Window initialisation.
        self.root_window = tk.Tk()
        self.root_window.title = "Subtitle Corrector GUI"
        self.root_window.geometry("400x150")
        # File selection.
        self.file_frame = tk.Frame(master=self.root_window, width=100, height=100)
        self.sfile_path_label = tk.Label(
            master=self.file_frame,
            text="Subtitle file: ",
        )
        self.path_entry = tk.Entry(
            master=self.file_frame,
            width=40,
            state="readonly"
        )
        self.sfile_button = tk.Button(
            master=self.file_frame,
            text="Select subtitle file...",
            command=self.choose_file
        )
        self.sfile_status_label = tk.Label(
            master=self.file_frame,
            text="Status: processing not started",
        )
        self.sfile_process_button = tk.Button(
            master=self.root_window,
            text="No file yet selected",
            command=self.process_subtitle,
            state=tk.DISABLED
        )
        self.path_entry.config(readonlybackground=self.path_entry.cget("background"))
        self.file_frame.pack(fill=tk.X)
        self.sfile_path_label.pack()
        self.path_entry.pack()
        self.sfile_button.pack()
        self.sfile_status_label.pack()
        self.sfile_process_button.pack()


def main():
    SRT_corrector = SRTCorrectorGui()
    SRT_corrector.root_window.mainloop()

main()
