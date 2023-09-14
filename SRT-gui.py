#!/usr/bin/env python3

import subtitlecorrector as stc
import tkinter as tk
from tkinter import filedialog
import platform

class SRTCorrectorGui:
    # Process file.
    def process_subtitle(self):
        if (self.full_output_path != "" and self.subtitle_file_path != ""):
            self.sfile_status_label.config(text="Processing started...")
            subtitles_list = stc.srt_to_text(self.subtitle_file_path)
            stc.correct_subtitles(subtitles_list, self.full_output_path)
            self.sfile_status_label.config(text="Processing completed.")
        else:
            self.sfile_status_label.config(text="Please select the path to the input subtitle and the path for the output.")

    # Select file.
    def choose_file(self):
        self.subtitle_file_path = filedialog.askopenfilename()
        if self.subtitle_file_path:
            self.path_entry.config(state="normal")
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.subtitle_file_path)
            self.path_entry.config(state="readonly")
            self.sfile_process_button.config(state="normal", text="Process subtitle file")

    def choose_odir(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            if (platform.system() == "Linux" or platform.system() == "Darwin"):
                self.full_output_path = self.output_dir + "/" + "output.srt"
            else:
                self.full_output_path = self.output_dir + "\\" + "output.srt"
            self.ofile_path.config(state="normal")
            self.ofile_path.delete(0, tk.END)
            self.ofile_path.insert(0, self.full_output_path)
            self.ofile_path.config(state="readonly")
            open(self.full_output_path, "w+")


    # Sets up the GUI for selecting a file.
    def file_selection_GUI(self):
        self.file_frame = tk.Frame(master=self.root_window, width=100, height=100)
        self.sfile_path_label = tk.Label(master=self.file_frame, text="Subtitle file: ")
        self.path_entry = tk.Entry(master=self.file_frame, width=40, state="readonly")
        self.sfile_button = tk.Button(
            master=self.file_frame,
            text="Select...",
            command=self.choose_file
        )
        self.path_entry.config(readonlybackground=self.path_entry.cget("background"))
        self.file_frame.pack(fill=tk.X)
        self.sfile_path_label.pack(padx=10, side="left")
        self.path_entry.pack(padx=10, side="left")
        self.sfile_button.pack(padx=10, side="left")

    def ofile_selection_GUI(self):
        self.outputfile_frame = tk.Frame(master=self.root_window, width=100, height=100)
        self.ofile_label = tk.Label(master=self.outputfile_frame, text="Output folder:")
        self.ofile_path = tk.Entry(master=self.outputfile_frame, width=40, state="readonly")
        self.ofile_button = tk.Button(
            master=self.outputfile_frame,
            text="Select...",
            command=self.choose_odir
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
        self.subtitle_file_path = ""
        self.full_output_path = ""
        self.output_dir = ""
        # Window initialisation.
        self.root_window = tk.Tk()
        self.root_window.title = "Subtitle Corrector GUI"
        self.root_window.geometry("425x150")

        self.file_selection_GUI()
        self.ofile_selection_GUI()
        self.processing_GUI()
        self.license_label = tk.Label(self.root_window, text="Subtitle Corrector is Free Software licensed under the GNU GPLv3")
        self.license_label.pack(side="bottom")



def main():
    SRT_corrector = SRTCorrectorGui()
    SRT_corrector.root_window.mainloop()

main()
