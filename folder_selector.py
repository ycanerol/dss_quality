from tkinter import filedialog
from tkinter import *


def folder_selector():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(initialdir='~')
    return folder_selected
