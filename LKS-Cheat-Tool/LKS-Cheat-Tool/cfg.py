import tkinter
from tkinter import ttk
from tkinter import *

root = Tk()
ver_num = "0.9.0_dev"
root.title("LKS Cheat Tool v" + ver_num)
main_frame = ttk.Frame(root, padding=10)
main_frame.grid()
top_menu = ttk.Notebook(main_frame)

curr_chapter = IntVar()
castle_level = IntVar()
lks_region = "NTSC-U"
removable_vars = []
mode = "Waiting"
save_file = 0

loading_frame = ttk.Frame(main_frame)
loading_frame.grid(column=1, row=0)
Label(loading_frame, text="Waiting for LKS...").grid(column=0, row=0)
bar = ttk.Progressbar(loading_frame, mode='indeterminate', length=100)
bar.grid(column=1, row=0)
bar.start(15)

save_edit_button = ttk.Button(main_frame, text="Start Save Editor", width=25)
live_button = ttk.Button(main_frame, text="Start Live Mode", state=['disabled'], width=25)
quit_button = ttk.Button(main_frame, text="Quit", command=root.quit, width=15)
save_edit_button.grid(column=0, row=0, sticky='ew')
live_button.grid(column=1, row=0, sticky='ew')
quit_button.grid(column=4, row=0, sticky='e')

loading_frame.tkraise()

def gimme_a_function_with_nothing(*args):
    pass