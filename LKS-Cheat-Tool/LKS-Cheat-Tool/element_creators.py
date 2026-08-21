from file_readers import *
from memory_modifiers import *
import cfg

import tkinter
from tkinter import *
from tkinter import ttk
from functools import partial

def create_flag_box(flag, var, frame, name="none", image=""):
    
    flipper = partial(flip_flag, flag)
    if image != "":
        checkbox = ttk.Checkbutton(frame, image=image, command=flipper, variable=var)
    else:
        checkbox = ttk.Checkbutton(frame, text=name, command=flipper, variable=var)
    if flag == -1:
        checkbox.configure(state=['disabled'])
    else:
        update_loop("bit_flag", flag, var)
    return checkbox

def create_scroll_frame(upper_frame, column, row, width, height, columnspan=1, rowspan=1):
    
    canvas = Canvas(upper_frame, width=width, height=height)
    frame = Frame(canvas)
    canvas.create_window(0, 0, window=frame, anchor='nw')
    canvas.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    scroller = ttk.Scrollbar(upper_frame, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=scroller.set)
    scroller.grid(column=column+columnspan+1, row=row, rowspan=rowspan, sticky='ns')

    return frame

def create_live_entry(frame, mode, pos, state=['normal']):
    
    if mode == "word":
        bol = IntVar()
        bol.trace_add("write", partial(word_write, bol, pos))
        update_loop("word", pos, bol)
    if mode == "float":
        bol = DoubleVar()
        bol.trace_add("write", partial(float_write, bol, pos))
        update_loop("float", pos, bol)
    return ttk.Entry(frame, textvariable=bol, state=state)

def view_inv_slot(*args):
    
    frame = args[2]    
    slot = args[0]
    id = dolphin_memory_engine.read_bytes(get_save_pos(0x9041E7A4 + (2 * slot)), 2)
    name_key = args[1]
    name = StringVar(value=read_table(name_key, str(int(id.hex(), 16))))
    Label(frame, text="Inventory Slot "+str(slot+1)+": ").grid(column=0, row=slot, sticky='w')
    selector = ttk.Combobox(frame, textvariable=name)
    selector.grid(column=1, row=slot)
    selector['values'] = name_key[1]
    selector.bind('<<ComboboxSelected>>', partial(id_write, name, name_key, 0x9041E7A4 + (2 * slot)))
    update_loop("id", 0x9041E7A4 + (2 * slot), name, name_key)
    
def view_citizen(*args):
    
    frame = args[0]
    for info in frame.winfo_children():
        if frame.winfo_children().index(info) > 1:
            info.destroy()
    
    slot = int(args[1].get())
    offset = get_save_pos(0x903F6B20 + (452 * slot))
    
    name_db = args[2]
    job_db = args[3]
    item_db = args[4]
    
    index = 0
    
    floats = [["X Position", 20, ['normal']], ["Y Position", 24, ['normal']], ["Z Position", 28, ['normal']], ["Rotation", 32, ['readonly']]]
    vars = []
    partials = []
    
    if args[5] == 'full':
        for flt in floats:
            vars.insert(0, DoubleVar(value=dolphin_memory_engine.read_float(get_save_pos(offset+flt[1]))))
            Label(frame, text=flt[0]).grid(column=0, row=index)
            Entry(frame, textvariable=vars[0], state=flt[2]).grid(column=1, row=index)
            partials.insert(0, partial(float_write, vars[0], offset+flt[1]))
            vars[0].trace_add('write', partials[0])
            update_loop("float", offset+flt[1], vars[0])
            index += 1
    
    index = 0
    ids = [["Name", 8, name_db, ['normal']], ["Job", 235, job_db, ['normal']], ["Hat", 38, item_db, ['normal']], ["Held Item", 36, item_db, ['normal']], ["Equipment", 40, item_db, ['normal']]]
    dropdowns = []
    
    for id in ids:
        slot = dolphin_memory_engine.read_bytes(get_save_pos(offset+id[1]), 2)
        slot = int(slot.hex(), 16)
        if len(id[2]) > 2:
            names = id[2]
            if slot >= len(names):
                slot = len(names) - 1
            vars.insert(0, StringVar(value=names[slot]))
        else:
            names = id[2][1]
            vars.insert(0, StringVar(value=read_table(id[2], str(slot))))
        Label(frame, text=id[0]).grid(column=2, row=index)
        dropdowns.insert(0, ttk.Combobox(frame, textvariable=vars[0], state=id[3]))
        dropdowns[0].grid(column=3, row=index)
        partials.insert(0, partial(id_write, vars[0], id[2], offset+id[1]))
        dropdowns[0]['values'] = names
        dropdowns[0].bind('<<ComboboxSelected>>', partials[0])
        update_loop("id", offset+id[1], vars[0], id[2])
        index += 1
    
    if args[5] == 'full':
        tp = partial(teleport, [offset + 20, offset + 24, offset + 28], ["corobo"])
        ttk.Button(frame, text = "Warp to Me!", command = tp).grid(column=1, row=4, sticky='ew')

def find_and_build_citizen(*args):
    
    var = args[0]
    frame = args[1]
    name_db = args[2]
    job_db = args[3]
    item_db = args[4]
    
    for info in frame.winfo_children():
        info.destroy()

    if var.get() != 0:
        index = 0
        chartype = 0
        while (chartype != var.get()) & (index < 500):
            chartype = dolphin_memory_engine.read_word(get_save_pos(0x903F6B20 + (452 * index)))
            index += 1
        index -= 1
        if index < 499:
            view_citizen(frame, IntVar(value=index), name_db, job_db, item_db, 'partial')
        else:
            Label(frame, text = "oh nooooooo").grid(column=0, row=0)


def teleport(var_array, coord_array, grid_array = []):

    if coord_array[0] != "corobo":
        for i in list(range(3)):
            if coord_array[0] != "grid":
                if coord_array[i] != "same":
                    dolphin_memory_engine.write_float(var_array[i], coord_array[i])
            else:
                if grid_array[i] != "same":
                    dolphin_memory_engine.write_float(var_array[i], (grid_array[i].get()*64)+32)
    else:
        dolphin_memory_engine.write_bytes(var_array[0], dolphin_memory_engine.read_bytes(get_save_pos(0x903f6b34), 12))
        dolphin_memory_engine.write_bytes(var_array[0]+28, dolphin_memory_engine.read_bytes(get_save_pos(0x903f6b50), 16))


def update_loop(type, pos, var, db=[]):

    if type == "bit_flag":
        var.set(check_flag(pos))
        
    if type == "byte":
        var.set(dolphin_memory_engine.read_byte(get_save_pos(pos)))
        
    if type == "word":
        new = dolphin_memory_engine.read_word(get_save_pos(pos))
        if var.get() != new:
            var.set(new)
            
    if type == "float":
        var.set(dolphin_memory_engine.read_float(get_save_pos(pos)))

    if type == "id":
        value = int(dolphin_memory_engine.read_bytes(get_save_pos(pos), 2).hex(), 16)
        if isinstance(db[0], str):
            if value >= len(db):
                value = len(db) - 1
            var.set(db[value])
        else:
            var.set(read_table(db, str(value)))

    looper = partial(update_loop, type, pos, var, db)

    if type == "float":
        cfg.root.after(100, looper)
    else:
        cfg.root.after(1000, looper)