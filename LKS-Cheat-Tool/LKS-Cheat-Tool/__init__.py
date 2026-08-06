import dolphin_memory_engine
import tkinter
import time
import threading
import fileinput
from tkinter import *
from tkinter import ttk
from functools import partial
from fileinput import FileInput
from os import path
from os import listdir

def lks_hook():
    
    global root
    hooked = False
    
    dolphin_memory_engine.hook()
    
    if (dolphin_memory_engine.is_hooked()):
        if (dolphin_memory_engine.read_bytes(0x80000000, 6) == b"RO3EXJ") | (dolphin_memory_engine.read_bytes(0x80000000, 6) == b"RO3P99"):
            hooked = True
    
    if not(hooked):
        dolphin_memory_engine.un_hook()
        root.after(1000, lks_hook)
    else:
        enable_all(root)
        
def enable_all(section):
    for widget in section.winfo_children():
        type = widget.widgetName
        if type == "ttk::notebook":
            for tab in widget.winfo_children():
                widget.tab(tab, state=['normal'])
        else:
            if (type != "ttk::frame") & (type != "ttk::labelframe") & (type != "frame") & (type != "ttk::canvas") & (type != "ttk::scrollbar") & (type != "ttk::progressbar"):
                widget.configure(state=['normal'])
        if widget.winfo_children != []:
            enable_all(widget)
            
def disable_all(section):
    
    for widget in section.winfo_children():
        type = widget.widgetName
        if type == "ttk::notebook":
            for tab in widget.winfo_children():
                widget.tab(tab, state=['disabled'])
        else:
            if (type != "ttk::frame") & (type != "ttk::labelframe") & (type != "frame") & (type != "ttk::canvas") & (type != "ttk::scrollbar") & (type != "ttk::progressbar"):
                widget.configure(state=['disabled'])
        if widget.winfo_children != []:
            disable_all(widget)

def get_save_pos(location):
    
    init_save_pos = 0x903E8900
    if dolphin_memory_engine.read_bytes(0x80000000, 6) == b"RO3EXJ":
        save_pos_ptr = 0x8055759C
    else:
        save_pos_ptr = 0x80555ABC   
    curr_save_pos = dolphin_memory_engine.read_word(save_pos_ptr)
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
        flag_start = get_save_pos(0x9041A971)
        flag_position = flag_start + (args[0].get() // 8)
        hex_value = dolphin_memory_engine.read_byte(flag_position)
        if args[1].get():
            dolphin_memory_engine.write_byte(flag_position, hex_value | (2**(args[0].get() % 8)))
        else:
            dolphin_memory_engine.write_byte(flag_position, hex_value & ~(2**(args[0].get() % 8)))

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
    
def assign_bol(*args):

    bol = args[0].get()
    if (bol != "") & (bol <= 2**32):
        dolphin_memory_engine.write_word(get_save_pos(0x9041B350), bol)

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

def view_inv_slot(*args):
    
    frame = args[2]    
    slot = args[0]
    id = dolphin_memory_engine.read_bytes(get_save_pos(0x9041E7A4 + (2 * slot)), 2)
    name_key = args[1]
    name = StringVar(value=read_table(name_key, str(int(id.hex(), 16))))
    Label(frame, text="Inventory Slot "+str(slot+1)+": ").grid(column=0, row=slot)
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
        ttk.Button(frame, text = "Warp to Me!", command = tp).grid(column=1, row=4)

def find_and_build_citizen(*args):
    
    var = args[0]
    frame = args[1]
    name_db = args[2]
    job_db = args[3]
    item_db = args[4]
    
    for info in frame.winfo_children():
        if frame.winfo_children().index(info) > 1:
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

def list_file_read(filename):
    
    output = []
    file = fileinput.input(files=filename)
    for line in file:
        output.append(line.rstrip())
        
    return output

def keygen(filename):
    
    keys = []
    outputs = []
    file = fileinput.input(files=filename+".tsv", encoding='utf-8')
    for line in file:
        divorce = line.split('\t')
        divorce.append("")
        keys.append(divorce[0].rstrip())
        outputs.append(divorce[1].rstrip())
        
    return [keys, outputs]

def read_table(table, key):
    
    key_set = table[0]
    output_set = table[1]
    
    if (key_set.count(key)) > 0:
        result = output_set[key_set.index(key)]
    else:
        result = "Not Found"
    
    return result
    
def wait_for_hook():
    
    global root
    if len(root.winfo_children()) == 1:
        loading_frame = ttk.Frame(root)
        loading_frame.grid(column=0, row=0)
        Label(loading_frame, text="Waiting for LKS...").grid(column=0, row=0)
        bar = ttk.Progressbar(loading_frame, mode='indeterminate', length=200)
        bar.grid(column=1, row=0)
        bar.start(15)
        
    if dolphin_memory_engine.is_hooked():
        root.winfo_children()[1].destroy()
        construct_inventory_menu()
        construct_citizens_menu()
        construct_kingdom_plan_menu()
        construct_debug_menu()
    else:
        root.after(1000, wait_for_hook)

def construct_top_menu():
    
    global root
    frame = root.winfo_children()[0]
    
    top_menu = ttk.Notebook(frame)
    top_menu.grid(column=0, row=2)
    top_menu_tabs=[[ttk.Frame(top_menu), "General"], [ttk.Frame(top_menu), "Game State"], [ttk.Frame(top_menu), "Citizens"], [ttk.Frame(top_menu), "Kingdom Plans"], [ttk.Frame(top_menu), "Advanced"]]
    for tab in top_menu_tabs:
        top_menu.add(tab[0], text=tab[1])
        
def construct_inventory_menu():
    
    global root
    slot = 1
    inv_top_menu_tab = root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
    ttk.Label(inv_top_menu_tab, text="Bol Count").grid(column=0, row=0)
    bol = IntVar(value=0)
    bol_send = partial(assign_bol, bol)
    bol_entry = ttk.Entry(inv_top_menu_tab, textvariable=bol)
    bol_entry.grid(column=0, row=1)
    bol.trace_add("write", bol_send)
    update_loop("word", 0x9041B350, bol)
    
    standard_inventory = ttk.Labelframe(inv_top_menu_tab, text="Inventory")
    standard_inventory.grid(column=1, row=0, rowspan=10)
    inv_scroll_frame = create_scroll_frame(standard_inventory, 0, 0, 300, 225)
    inventory_contents = keygen(path.abspath(path.dirname(__file__)+"/Tables/Items"))
    for i in list(range(100)):
        view_inv_slot(i, inventory_contents, inv_scroll_frame)
    
    global key_item_images
    key_item_images = []
    key_item_image_names = listdir(path.abspath(path.dirname(__file__)+"/Images/Key_Items"))
    for image in key_item_image_names:
        key_item_images.append(PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/Key_Items/"+image)))
    
    key_item_notebook = ttk.Notebook(inv_top_menu_tab)
    key_item_notebook.grid(column=0, row=11, columnspan=2)
    key_item_tabs = [["Letters & Memos", "", -1], ["Flying Machine", "", -1], ["Art Pieces", "Art Gallery", 488], ["Wonder Spots", "Book - Wonder Spot", 480], ["UMA Research", "Book - UMA", 481], ["Delicacy Discovery", "Book - Gourmet", 482], ["Animal Rescue", "Book - Animal", 483], ["Hum Discography", "Book - Tunesmith", 484], ["Kingstone Collection", "Book - Jewel", 485], ["Record Smashing", "Book - Records", 486], ["Cutscenes", "Book - Video Archive", -1]]
    key_item_frames = []
    for tab in key_item_tabs:
        key_item_frames.insert(0, ttk.Frame(key_item_notebook))
        key_item_notebook.add(key_item_frames[0], text=tab[0])
        if tab[1] != "":
            for jpg in key_item_images:
                if jpg.cget('file').find(tab[1]) != -1:
                    Label(key_item_frames[0], image = jpg).grid(column=0, row=0)
        if tab[2] != -1:
            if tab[1].find("Book") != -1:
                create_flag_box(tab[2], BooleanVar(), key_item_frames[0], tab[1].removeprefix("Book - ")+"\nBook Enabled").grid(column=1, row=0)
            else:
                create_flag_box(tab[2], BooleanVar(), key_item_frames[0], tab[1] +"\nEnabled").grid(column=1, row=0)
    key_item_frames.reverse()

    bools = []
    
    curr_frame = key_item_frames[0]
    entries = [[489, "Onii King"], [490, "Duvroc"], [491, "Shishkebaboo"], [492, "Omelet"], [493, "TV Dinnah"], [494, "Long Sauvage"], [495, "Jumbo Champloon"], [-1, "Onii King"], [-1, "Duvroc"], [-1, "Shishkebaboo"], [-1, "Omelet"], [-1, "TV Dinnah"], [-1, "Long Sauvage"], [-1, "Jumbo Champloon"]]
    index = 0
    for slot in entries:
        bools.insert(0, BooleanVar())
        if index < 7:
            name = "Letter - " + slot[1]
        else:
            name = "God Memo - " + slot[1]
        for jpg in key_item_images:
            if jpg.cget('file').find(name) != -1:
                image = jpg
        Label(curr_frame, text=name.replace(" - ", "\n")).grid(column=index%7, row=2*(index//7))
        create_flag_box(slot[0], bools[0], curr_frame, name, image).grid(column=index%7, row=(2*(index//7))+1)
        index += 1
    
    curr_frame = key_item_frames[1]
    entries = keygen(path.abspath(path.dirname(__file__)+"/Tables/Flying_Machine"))
    for i in list(range(len(entries[0]))):
        bools.insert(0, BooleanVar())
        name = entries[1][i]
        for jpg in key_item_images:
            if jpg.cget('file').find(name) != -1:
                image = jpg
        if i == 0:
            Label(curr_frame, text=name).grid(column=0, row=0)
            create_flag_box(int(entries[0][i]), bools[0], curr_frame, name, image).grid(column=0, row=1, rowspan=3)
        if i == 7:
            Label(curr_frame, text=name).grid(column=3, row=2, columnspan=2)
            create_flag_box(int(entries[0][i]), bools[0], curr_frame, name, image).grid(column=3, row=3, columnspan=2)
        if (i != 0) & (i < 5):
            Label(curr_frame, text=name).grid(column=i, row=0)
            create_flag_box(int(entries[0][i]), bools[0], curr_frame, name, image).grid(column=i, row=1)
        if (i > 4) & (i != 7):
            Label(curr_frame, text=name).grid(column=i-4, row=2)
            create_flag_box(int(entries[0][i]), bools[0], curr_frame, name, image).grid(column=i-4, row=3)
    
    curr_frame = create_scroll_frame(key_item_frames[2], 0, 1, 1168, 425, 2, 1)
    if dolphin_memory_engine.read_bytes(0x80000000, 6) == b"RO3EXJ":
        entries = keygen(path.abspath(path.dirname(__file__)+"/Tables/Art_US"))
    else:
        entries = keygen(path.abspath(path.dirname(__file__)+"/Tables/Art_EU"))
    for i in list(range(len(entries[0]))):
        bools.insert(0, BooleanVar())
        name = entries[1][i]
        key_item_images.insert(0, PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/Art/"+name.replace('\\n', ' ').replace('*', 'ASTERISK')+".png")))
        Label(curr_frame, text=name.replace("\\n", "\n")).grid(column=i%10, row=1+(2*(i//10)))
        create_flag_box(int(entries[0][i]), bools[0], curr_frame, name, key_item_images[0]).grid(column=i%10, row=2+(2*(i//10)))

    books = [[3, "/Tables/Wonder_Spots", (0x9041e71a * 8) + 1, "Wonder_Spots", 10], [4, "/Tables/UMA_Logs", 0, "UMA_Pages", 12], [5, "/Tables/Gourmet_Entries", 0, "Gourmet_Pages", 10], [6, "/Tables/Animals", (0x9041e76a * 8) + 1, "Animal_Entries", 7], [7, "/Tables/Hums", (0x9041e73a * 8) + 1, "Hum_Pages", 10], [8, "/Tables/Kingstones", (0x9041e75a * 8) + 1, "Kingstones", 7], [10, "/Tables/Cutscenes", (0x9041e72a * 8) + 1, "Cutscene_Thumbnails", 9]]
    for book in books:
        curr_frame = key_item_frames[book[0]]
        entries = keygen(path.abspath(path.dirname(__file__)+book[1]))
        offset = book[2]
        width = book[4]
        for i in list(range(len(entries[0]))):
            bools.insert(0, BooleanVar())
            name = entries[1][i]
            key_item_images.insert(0, PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/"+book[3]+"/"+name.replace("?", "QMARK")+".png")))
            Label(curr_frame, text=name).grid(column=i%width, row=1+(2*(i//width)))
            create_flag_box(offset + int(entries[0][i]), bools[0], curr_frame, name, key_item_images[0]).grid(column=i%width, row=2+(2*(i//width)))
    
def construct_citizens_menu():
    
    global root
    slot = 3
    citizens_top_menu_tab = root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
    index = 24
    while (dolphin_memory_engine.read_word(get_save_pos(0x903F6B20 + (452 * index))) != 0):
        offset = 0x903F6B20 + (452 * index)
        index+=1
    
    ttk.Label(citizens_top_menu_tab, text="Citizen Number").grid(column=0, row=0)
    selected_slot = StringVar()
    citizen_selector = ttk.Combobox(citizens_top_menu_tab, textvariable=selected_slot)
    citizen_selector['values'] = tuple(range(index))
    citizen_selector.grid(column=1, row=0)
    citizen_readout = ttk.Labelframe(citizens_top_menu_tab, text="Selected")
    citizen_readout.grid(column=0, row=1, columnspan=2)
    name_key = list_file_read(path.abspath(path.dirname(__file__)+"/Lists/Names"))
    job_key = keygen(path.abspath(path.dirname(__file__)+"/Tables/Job_IDs"))
    item_key = keygen(path.abspath(path.dirname(__file__)+"/Tables/Items"))
    citizen_peek = partial(view_citizen, citizen_readout, selected_slot, name_key, job_key, item_key, 'full')
    citizen_selector.bind('<<ComboboxSelected>>', citizen_peek)
    
    rg_section = ttk.Labelframe(citizens_top_menu_tab, text="Royal Guard")
    rg_section.grid(column=2, row=0, rowspan=5)
    rg_subframes = []
    chartypes = []
    partials = []
    for index in list(range(30)):
        rg_subframes.append(ttk.Labelframe(rg_section, text = "Slot " + str(index+1)))
        slot = 0x92BC4310 + (index * 1736)
        chartypes.append(IntVar(value=0))
        partials.append(partial(find_and_build_citizen, chartypes[index], rg_subframes[index], name_key, job_key, item_key))
        chartypes[index].trace_add('write', partials[index])
        update_loop("word", slot+648, chartypes[index])
        rg_subframes[index].grid(column=index%3, row=1+(index//3))

def construct_kingdom_plan_menu():
    
    global root
    slot = 4
    kp_top_menu_tab = root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
   
    kingdom_plan_menu = ttk.Notebook(kp_top_menu_tab)
    global tab_images
    tab_images=[]
    tab_frames=[]
    kingdom_plan_categories = ["Special", "Power Up", "Castle Town", "Grassland Town", "Farmland", "Stone City", "Soldier Town", "Gourmet Town", "Royal City", "Glamour Town", "Miner\'s Town", "Magical Land (Category)"]
    for tab in kingdom_plan_categories:
        tab_images.insert(0, PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/Kingdom_Plan/"+tab+".png")))
        tab_frames.insert(0, ttk.Frame(kingdom_plan_menu))
        if tab != "Magical Land (Category)":
            kingdom_plan_menu.add(tab_frames[0], text=tab)
        else:
            kingdom_plan_menu.add(tab_frames[0], text="Magical Land")
        Label(tab_frames[0], image=tab_images[0]).grid(column=0, row=0)
    tab_frames.reverse()
    kingdom_plan_menu.grid(column=0, row=0)
    
    kingdom_plan_flags = [519, 521, 522, 523, 524, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 543, 544, 545, 546, 547, 548, 549, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 938, 939, 940, 941, 942, 943, 944, 991, 992, 993, 994, 995, 996]
    kingdom_plan_names = ["Flower Appointee", "Podium Placement", "Modify Podium", "Defense Formation", "Evade Formation", "Video Archive", "Weapons Research", "Armor Research", "Super Weapons", "Super Armor", "Jump Cannon", "School Donation 1", "School Donation 2", "School Donation 3", "School Donation 4", "School Donation 5", "School Donation 6", "School Donation 7", "Rare Armor", "Alarm Clock", "Guard Badge x3", "Guard Badge x4", "Guard Badge x5", "Guard Badge x6", "Guard Badge x7", "Farmhouse", "Guard House", "Town Square", "Soup Church", "Red-Roof House", "Yellow-Roof House", "Blue-Roof House", "Straw-Roof House", "Carpenter Hut", "Southern Village", "Northern Village", "Hunter Hut", "Riverside Cabin", "Floral Florist", "Moon Harvest", "Lumberjack Hut", "Shopping Arcade", "Stonecutter Village", "Furniture Factory", "Stonecutting Plant", "Uptight Residence", "Lively Residence", "Jolly Residence", "Veteran\'s Barracks", "Fruit Farm Village", "Culinary Academy (Gourmet Town)", "Gourmet Residence", "Royal School", "Royal Florist", "Culinary Academy (Royal City)", "Royal Heights", "Royal Terrace", "Royal Place", "Royal Hills", "Royal Residence", "Royal Tower", "Marvelous Theater", "Gorgeous Residence", "Deluxe Residence", "Rock Head Village", "Machine Residence", "Giga Grinder", "Let\'s Play! Panel", "Magical Land", "Calisthenics Edict", "Dash Ordinance", "Jumping Jack Edict", "Give Crunchy Beans", "Give Pow Beans", "Give Muscle Beans"]
    kingdom_plan_placements = [0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 1, 1, 1, 1, 1, 1]
    
    global kingdom_plans
    kingdom_plans = []
    index = 0
    for flag in kingdom_plan_flags:
        if kingdom_plan_names[index].startswith("Culinary Academy"):
            kingdom_plans.append([flag, "Culinary Academy", PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/Kingdom_Plan/"+kingdom_plan_names[index]+".png")), BooleanVar(value=check_flag(flag)), kingdom_plan_placements[index]])
        else:
            kingdom_plans.append([flag, kingdom_plan_names[index], PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/Kingdom_Plan/"+kingdom_plan_names[index]+".png")), BooleanVar(value=check_flag(flag)), kingdom_plan_placements[index]])
        index+=1
    
    index = 0
    for plan in kingdom_plans:
        c = kingdom_plan_placements[0:index].count(plan[4])
        create_flag_box(plan[0], plan[3], tab_frames[plan[4]], plan[1], plan[2]).grid(column=c%9, row=2+(2*(c//9)))
        ttk.Label(tab_frames[plan[4]], text=plan[1]).grid(column=c%9, row=1+(2*(c//9)))
        index += 1
    
def construct_debug_menu():
    
    global root
    slot = 5
    debug_top_menu_tab = root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
    bit_frame = ttk.Labelframe(debug_top_menu_tab, text="Bit Flags")
    counter_frame = ttk.Labelframe(debug_top_menu_tab, text="Counter Flags")
    bit_frame.grid(column=0, row=0)
    counter_frame.grid(column=1, row=0)
    
    Label(bit_frame, text="Flag").grid(column=0, row=0)
    Label(bit_frame, text="Enabled?").grid(column=1, row=0)
    
    flag = IntVar(value=0)
    set = BooleanVar()
    Entry(bit_frame, textvariable=flag, width=4).grid(column=0, row=1)
    ttk.Checkbutton(bit_frame, variable=set).grid(column=1, row=1)
    flag_name = StringVar(value="")
    flag_name_label = Label(bit_frame, text=flag_name.get())
    flag_name_label.grid(column=0, row=2)
    read_bit_flag = partial(flag_readout, flag, flag_name, set, flag_name_label)
    flag.trace_add('write', read_bit_flag)
    flipper = partial(set_flag, flag, set)
    ttk.Button(bit_frame, text="Send!", command=flipper).grid(column=1, row=2)
    
    Label(counter_frame, text="Flag").grid(column=0, row=0)
    Label(counter_frame, text="Value").grid(column=1, row=0)
    
    cflag = IntVar(value=0)
    cset = IntVar(value=0)
    Entry(counter_frame, textvariable=cflag, width=3).grid(column=0, row=1)
    Entry(counter_frame, textvariable=cset, width=3).grid(column=1, row=1)
    cflag_name = StringVar(value="")
    cflag_name_label = Label(counter_frame, text=cflag_name.get())
    cflag_name_label.grid(column=0, row=2)
    read_counter_flag = partial(cflag_readout, cflag, cflag_name, cset, cflag_name_label)
    cflag.trace_add('write', read_counter_flag)
    csetter = partial(set_cvar, cflag, cset)
    ttk.Button(counter_frame, text="Send!", command=csetter).grid(column=1, row=2)

    teleport_frame = ttk.Labelframe(debug_top_menu_tab, text="Teleport")
    teleport_frame.grid(column=2, row=0)
    
    xgrid = IntVar(value=0)
    zgrid = IntVar(value=0)
    Label(teleport_frame, text= "N/S Grid").grid(column=0, row=0)
    Label(teleport_frame, text= "E/W Grid").grid(column=1, row=0)
    Entry(teleport_frame, textvariable=zgrid, width=2).grid(column=0, row=1)
    Entry(teleport_frame, textvariable=xgrid, width=2).grid(column=1, row=1)
    tp = partial(teleport, [get_save_pos(0x903F6B34), get_save_pos(0x903F6B38), get_save_pos(0x903F6B3C)], ["grid"], [xgrid, "same", zgrid])
    ttk.Button(teleport_frame, text="Send!", command=tp).grid(column=1, row=2)

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

    global root

    if type == "bit_flag":
        var.set(check_flag(pos))
        
    if type == "word":
        new = dolphin_memory_engine.read_word(get_save_pos(pos))
        if var.get() != new:
            var.set(new)
            
    if type == "float":
        var.set(dolphin_memory_engine.read_float(get_save_pos(pos)))
        
    if type == "id":
        if isinstance(db[0], str):
            var.set(db[int(dolphin_memory_engine.read_bytes(get_save_pos(pos), 2).hex(), 16)])
        else:
            var.set(read_table(db, str(int(dolphin_memory_engine.read_bytes(get_save_pos(pos), 2).hex(), 16))))
        
    looper = partial(update_loop, type, pos, var, db)
    
    if (type == "id") | (type == "flag"):
        root.after(1000, looper)
    else:
        root.after(100, looper)


global root
root = Tk()
root.title("LKS Cheat Tool")
frm = ttk.Frame(root, padding=10)
frm.grid()

construct_top_menu()

disable_all(root)
lks_hook()

wait_for_hook()

root.mainloop()

dolphin_memory_engine.un_hook()