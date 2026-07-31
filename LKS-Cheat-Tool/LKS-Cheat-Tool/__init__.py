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

def lks_hook():
    
    global root
    hooked = False
    
    dolphin_memory_engine.hook()
    
    if (dolphin_memory_engine.is_hooked()):
        if (dolphin_memory_engine.read_bytes(0x80000000, 6) == b"RO3EXJ"):
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

def check_flag(flag_index):
    
    if dolphin_memory_engine.is_hooked():
        flag_start = 0x9041A971
        flag_position = flag_start + (flag_index // 8)
        hex_value = dolphin_memory_engine.read_byte(flag_position)
        return (int(hex_value) & 2**(flag_index%8)) > 0
    else:
        return False

def flip_flag(flag_index):
    
    if dolphin_memory_engine.is_hooked():
        flag_start = 0x9041A971
        
        flag_position = flag_start + (flag_index // 8)
        
        hex_value = dolphin_memory_engine.read_byte(flag_position)
        
        is_active = ((int(hex_value) & 2**(flag_index%8))) > 0
        
        if (is_active):
            new_hex = ((int(hex_value) - 2**(flag_index%8)))
        else:
            new_hex = ((int(hex_value) + 2**(flag_index%8)))
    
        dolphin_memory_engine.write_byte(flag_position, new_hex)

def set_flag(*args):

    if dolphin_memory_engine.is_hooked():
        flag_start = 0x9041A971
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
        flag_start = 0x9041AC71
        flag_position = flag_start + args[0].get()
        dolphin_memory_engine.write_byte(flag_position, args[1].get())

def cflag_readout(*args):
    
    cflag = args[0]
    out_name = args[1]
    out_state = args[2]
    
    flag_table = keygen(path.abspath(path.dirname(__file__)+"/Tables/Counter_Flags"))
    name = read_table(flag_table, str(cflag.get()))
    state = int(dolphin_memory_engine.read_byte(cflag.get()+0x9041AC71))
    
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
        dolphin_memory_engine.write_word(0x9041B350, bol)

def view_inv_slot(*args):
    
    frame = args[2]    
    slot = args[0]
    id = dolphin_memory_engine.read_bytes(0x9041E7A4 + (2 * slot), 2)
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
    offset = 0x903F6B20 + (452 * slot)
    
    name_db = args[2]
    job_db = args[3]
    item_db = args[4]
    
    index = 0
    
    floats = [["X Position", 20, ['normal']], ["Y Position", 24, ['normal']], ["Z Position", 28, ['normal']], ["Rotation", 32, ['readonly']]]
    vars = []
    partials = []
    
    for flt in floats:
        vars.insert(0, DoubleVar(value=dolphin_memory_engine.read_float(offset+flt[1])))
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
        slot = dolphin_memory_engine.read_bytes(offset+id[1], 2)
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
        index += 1
    
    tp = partial(teleport, [offset + 20, offset + 24, offset + 28], [dolphin_memory_engine.read_float(0x903F6B34), dolphin_memory_engine.read_float(0x903F6B38), dolphin_memory_engine.read_float(0x903F6B3C)])
    ttk.Button(frame, text = "Warp to Me!", command = tp).grid(column=1, row=4)

def list_file_read(filename):
    
    output = []
    file = fileinput.input(files=filename)
    for line in file:
        output.append(line.rstrip())
        
    return output

def keygen(filename):
    
    keys = []
    outputs = []
    file = fileinput.input(files=filename)
    for line in file:
        divorce = line.split('\t')
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
    top_menu_tabs=[[ttk.Frame(top_menu), "Inventory"], [ttk.Frame(top_menu), "Citizens"], [ttk.Frame(top_menu), "Kingdom Plans"], [ttk.Frame(top_menu), "Advanced"]]
    for tab in top_menu_tabs:
        top_menu.add(tab[0], text=tab[1])
        
def construct_inventory_menu():
    
    global root
    slot = 1
    inv_top_menu_tab = root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
    bol_frame = Frame(inv_top_menu_tab)
    bol_frame.grid(column=0, row=0)
    ttk.Label(bol_frame, text="Bol Count").grid(column=0, row=0)
    bol = IntVar(value=0)
    bol_send = partial(assign_bol, bol)
    bol_entry = ttk.Entry(bol_frame, textvariable=bol)
    bol_entry.grid(column=0, row=1)
    bol.trace_add("write", bol_send)
    update_loop("word", 0x9041B350, bol)
    
    standard_inventory = ttk.Labelframe(inv_top_menu_tab, text="Inventory")
    standard_inventory.grid(column=2, row=0)
    inv_canvas = Canvas(standard_inventory, width=300, height=225)
    inv_scroll_frame = Frame(inv_canvas)
    inv_canvas.create_window(0, 0, window=inv_scroll_frame, anchor='nw')
    inv_canvas.grid(column=0, row=0)
    inv_scroll_frame.bind("<Configure>", lambda e: inv_canvas.configure(scrollregion=inv_canvas.bbox("all")))
    inventory_contents = keygen(path.abspath(path.dirname(__file__)+"/Tables/Items"))
    for i in list(range(100)):
        view_inv_slot(i, inventory_contents, inv_scroll_frame)
    inv_scroller = ttk.Scrollbar(standard_inventory, orient='vertical', command=inv_canvas.yview)
    inv_canvas.configure(yscrollcommand=inv_scroller.set)
    inv_scroller.grid(column=1, row=0, sticky='ns')
    
    global key_item_images
    key_item_images = []
    key_item_image_names = list_file_read(path.abspath(path.dirname(__file__)+"/Lists/Key_Item_Images"))
    for image in key_item_image_names:
        key_item_images.append(PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/Key_Items/"+image)))

def construct_citizens_menu():
    
    global root
    slot = 2
    citizens_top_menu_tab = root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
    index = 24
    while (dolphin_memory_engine.read_word(0x903F6B20 + (452 * index)) != 0):
        offset = 0x903F6B20 + (452 * index)
        index+=1
    
    selector_organizer = Frame(citizens_top_menu_tab)
    selector_organizer.grid(column=0, row=0)
    ttk.Label(selector_organizer, text="Citizen Number").grid(column=0, row=0)
    selected_slot = StringVar()
    citizen_selector = ttk.Combobox(selector_organizer, textvariable=selected_slot)
    citizen_selector['values'] = tuple(range(index))
    citizen_selector.grid(column=1, row=0)
    citizen_readout = ttk.Labelframe(citizens_top_menu_tab, text="Selected")
    citizen_readout.grid(column=0, row=1)
    name_key = list_file_read(path.abspath(path.dirname(__file__)+"/Lists/Names"))
    job_key = keygen(path.abspath(path.dirname(__file__)+"/Tables/Job_IDs"))
    item_key = keygen(path.abspath(path.dirname(__file__)+"/Tables/Items"))
    citizen_peek = partial(view_citizen, citizen_readout, selected_slot, name_key, job_key, item_key)
    citizen_selector.bind('<<ComboboxSelected>>', citizen_peek)

def construct_kingdom_plan_menu():
    
    global root
    slot = 3
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
        flip_plan = partial(flip_flag, plan[0])
        c = kingdom_plan_placements[0:index].count(plan[4])
        ttk.Checkbutton(tab_frames[plan[4]], image=plan[2], command=flip_plan, variable=plan[3]).grid(column=c%9, row=2+(2*(c//9)))
        ttk.Label(tab_frames[plan[4]], text=plan[1]).grid(column=c%9, row=1+(2*(c//9)))
        update_loop("bit_flag", plan[0], plan[3])
        index += 1
    
def construct_debug_menu():
    
    global root
    slot = 4
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
    ttk.Checkbutton(bit_frame, variable = set).grid(column=1, row=1)
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
    tp = partial(teleport, [0x903F6B34, 0x903F6B38, 0x903F6B3C], [], [xgrid, "same", zgrid])
    ttk.Button(teleport_frame, text="Send!", command=tp).grid(column=1, row=2)

def teleport(var_array, coord_array, grid_array = []):

    for i in tuple(range(3)):
        if len(grid_array) == 0:
            if coord_array[i] != "same":
                dolphin_memory_engine.write_float(var_array[i], coord_array[i])
        else:
            if grid_array[i] != "same":
                dolphin_memory_engine.write_float(var_array[i], (grid_array[i].get()*64)+32)

def update_loop(type, pos, var, db=[]):

    global root

    if type == "bit_flag":
        var.set(check_flag(pos))
        
    if type == "word":
        var.set(dolphin_memory_engine.read_word(pos))
            
    if type == "float":
        var.set(dolphin_memory_engine.read_float(pos))
        
    if type == "id":
        var.set(read_table(db, str(int(dolphin_memory_engine.read_bytes(pos, 2).hex(), 16))))
        
    looper = partial(update_loop, type, pos, var, db)
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