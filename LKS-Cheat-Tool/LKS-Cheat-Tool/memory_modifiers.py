from file_readers import *
import cfg

import dolphin_memory_engine
import tkinter
from tkinter import *

def get_save_pos(location):
    
    init_save_pos = 0x903E8900
    if cfg.lks_region == "NTSC-U":
        save_pos_ptr = 0x8055759C
    elif cfg.lks_region == "PAL":
        save_pos_ptr = 0x80555ABC
    curr_save_pos = dolphin_memory_engine.read_word(save_pos_ptr)
    if curr_save_pos == 0 or location < 0x90000000:
        curr_save_pos = 0x903E8900
    
    return location - init_save_pos + curr_save_pos

def check_flag(flag_index):
    
    if dolphin_memory_engine.is_hooked():
        flag_start = get_save_pos(0x9041A971)
        flag_position = flag_start + (flag_index // 8)
        if flag_index > 100000:
            flag_position = get_save_pos(flag_index // 8)
        hex_value = dolphin_memory_engine.read_byte(flag_position)
        return (int(hex_value) & 2**(flag_index%8)) > 0
    else:
        return False

def flip_flag(flag_index):
    
    if dolphin_memory_engine.is_hooked():
        flag_start = get_save_pos(0x9041A971)
        flag_position = flag_start + (flag_index // 8)
        if flag_index > 100000:
            flag_position = get_save_pos(flag_index // 8)
        hex_value = dolphin_memory_engine.read_byte(flag_position)
        is_active = ((int(hex_value) & 2**(flag_index%8))) > 0
        if (is_active):
            new_hex = ((int(hex_value) - 2**(flag_index%8)))
        else:
            new_hex = ((int(hex_value) + 2**(flag_index%8)))
        dolphin_memory_engine.write_byte(flag_position, new_hex)

def set_flag(*args):

    if dolphin_memory_engine.is_hooked():
        if not(isinstance(args[0], IntVar)) and not(isinstance(args[0], int)):
            new_args = args
            for i in args[0]:
                set_flag(i, args[1])
        else:
            if isinstance(args[0], IntVar):
                flag = args[0].get()
            else:
                flag = args[0]
            flag_start = get_save_pos(0x9041A971)
            flag_position = flag_start + (flag // 8)
            hex_value = dolphin_memory_engine.read_byte(flag_position)
            if args[1].get():
                dolphin_memory_engine.write_byte(flag_position, hex_value | (2**(flag % 8)))
            else:
                dolphin_memory_engine.write_byte(flag_position, hex_value & ~(2**(flag % 8)))

def flag_readout(*args):
    
    flag = args[0]
    out_name = args[1]
    out_state = args[2]
    
    flag_table = keygen(path.abspath(path.dirname(__file__)+"/Tables/Flags"))
    name = read_table(flag_table, str(flag.get()))
    state = check_flag(flag.get())
    
    out_name.set(name)
    out_state.set(state)
    
    args[3].configure(text=out_name.get())

def set_cvar(*args):
    
    if dolphin_memory_engine.is_hooked():
        flag_start = get_save_pos(0x9041AC71)
        flag_position = flag_start + args[0].get()
        dolphin_memory_engine.write_byte(flag_position, args[1].get())

def cflag_readout(*args):
    
    cflag = args[0]
    out_name = args[1]
    out_state = args[2]
    
    flag_table = keygen(path.abspath(path.dirname(__file__)+"/Tables/Counter_Flags"))
    name = read_table(flag_table, str(cflag.get()))
    state = int(dolphin_memory_engine.read_byte(get_save_pos(cflag.get()+0x9041AC71)))
    
    out_name.set(name)
    out_state.set(state)
    
    args[3].configure(text=out_name.get())

def id_write(new_result, db, pos, err=0):
    
    if not(isinstance(new_result, str)):
        new = new_result.get()
    else:
        new = new_result
    
    if len(db) > 2:
        new_id = db.index(new)
    else:
        new_id = db[0][db[1].index(new)]
    
    dolphin_memory_engine.write_byte(pos, int(new_id) // 256)
    dolphin_memory_engine.write_byte(pos+1, int(new_id) % 256)

def float_write(*args):
    
    var = args[0]
    pos = args[1]
    
    dolphin_memory_engine.write_float(pos, var.get())
    
def word_write(*args):

    dolphin_memory_engine.write_word(get_save_pos(args[1]), args[0].get())
    
def get_building(*args):
    
    index = args[0].get()
    mode = args[1]
    
    array_start = get_save_pos(0x903e8960)
    position = array_start + (index * 0x10c)
    
    curr_mode = dolphin_memory_engine.read_byte(position)
    
    if curr_mode == 0:
        mode.set("inactive")
    if curr_mode == 1:
        mode.set("sign")
    if curr_mode == 2:
        mode.set("built")
    
def set_building(i, mode):
    
    index = i.get()
    
    if mode.get() == "inactive":
        to_write = 0
    if mode.get() == "sign":
        to_write = 1
    if mode.get() == "built":
        to_write = 2
    
    array_start = get_save_pos(0x903e8960)
    position = array_start + (index * 0x10c)
    
    dolphin_memory_engine.write_byte(position, to_write)

def get_chapter():
    
    chapter_flag = 300
    
    for i in list(range(6)):
        if check_flag(chapter_flag + i):
            cfg.curr_chapter.set(i+1)
    
    cfg.root.after(1000, get_chapter)
            
def set_chapter(*args):
    
    new_chap = args[0]
    chapter_progress_flags = [[300], [301], [302], [303], [304], [305]]
    
    for set in chapter_progress_flags:
        for flag in set:
            set_flag(IntVar(value=flag), BooleanVar(value=False))
    
    for real in chapter_progress_flags[new_chap.get()-1]:
        set_flag(IntVar(value=real), BooleanVar(value=True))

def get_castle_level():
    
    castle_level_flag = 186
    
    for i in list(range(3)):
        if check_flag(castle_level_flag + i):
            cfg.castle_level.set(i)
    
    cfg.root.after(1000, get_castle_level)
            
def set_castle_level(*args):
    
    new_level = args[0]
    castle_level_flags = [[186], [187], [188]]
    
    for set in castle_level_flags:
        for flag in set:
            set_flag(IntVar(value=flag), BooleanVar(value=False))
    
    for real in castle_level_flags[new_level.get()]:
        set_flag(IntVar(value=real), BooleanVar(value=True))
    
    set_cvar(IntVar(value=4), IntVar(value=new_level.get()))
    