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
            if (type != "ttk::frame") & (type != "ttk::labelframe") & (type != "frame") & (type != "ttk::canvas") & (type != "ttk::scrollbar"):
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
            if (type != "ttk::frame") & (type != "ttk::labelframe") & (type != "frame") & (type != "ttk::canvas") & (type != "ttk::scrollbar"):
                widget.configure(state=['disabled'])
        if widget.winfo_children != []:
            disable_all(widget)

def check_flag(flag_index):
    
    if dolphin_memory_engine.is_hooked():
        flag_start = 0x9041A971
        flag_position = flag_start + (flag_index // 8)
        hex_value = dolphin_memory_engine.read_byte(flag_position)
        return BooleanVar(value = ((int(hex_value) & 2**(flag_index%8))) > 0)
    else:
        return BooleanVar(value = False)

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

def set_cvar(*args):
    
    if dolphin_memory_engine.is_hooked():
        flag_start = 0x9041AC71
        flag_position = flag_start + args[0].get()
        dolphin_memory_engine.write_byte(flag_position, args[1].get())
    
def assign_bol(*args):

    bol = args[0].get()
    if (bol != "") & (bol <= 2**32):
        dolphin_memory_engine.write_word(0x9041B350, bol)

def view_inv_slot(*args):
    
    global root
    frame = root.winfo_children()[0].winfo_children()[0].winfo_children()[0].winfo_children()[1]
    for info in frame.winfo_children():
        if frame.winfo_children().index(info) > 1:
            info.destroy()
    
    slot = int(args[0][0].get())
    id = dolphin_memory_engine.read_bytes(0x9041E7A4 + (2 * slot), 2)
    name_key = args[0][1]
    name = name_key[1][name_key[0].index(str(int(id.hex(), 16)))]
    Label(frame, text="Inventory Slot "+str(slot)).grid(column=0, row=2)
    Label(frame, text="ID: "+str(id.hex())).grid(column=0, row=3)
    Label(frame, text="Contents: "+name).grid(column=0, row=4)

def list_file_read(filename):
    
    output = []
    file = fileinput.input(files=filename)
    for line in file:
        output.append(line)
        
    return output

def keygen(filename):
    
    keys = []
    outputs = []
    file = fileinput.input(files=filename)
    for line in file:
        divorce = line.split('\t')
        keys.append(divorce[0])
        outputs.append(divorce[1])
        
    return [keys, outputs]

def construct_top_menu():
    
    global root
    frame = root.winfo_children()[0]
    
    top_menu = ttk.Notebook(frame)
    top_menu.grid(column=0, row=1)
    top_menu_tabs=[[ttk.Frame(top_menu), "Inventory"], [ttk.Frame(top_menu), "Citizens"], [ttk.Frame(top_menu), "Kingdom Plans"], [ttk.Frame(top_menu), "Debug"]]
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
    
    standard_inventory = ttk.Labelframe(inv_top_menu_tab, text="Inventory")
    standard_inventory.grid(column=2, row=0)
    ttk.Label(standard_inventory, text="Slot Number").grid(column=0, row=0)
    selected_slot = StringVar()
    inventory_selector = ttk.Combobox(standard_inventory, textvariable=selected_slot)
    inventory_selector.state(["readonly"])
    inventory_selector['values'] = tuple(range(100))
    inventory_selector.grid(column=0, row=1)
    inventory_contents = keygen(path.abspath(path.dirname(__file__)+"/Tables/Items"))
    inventory_peek = partial(view_inv_slot, [selected_slot, inventory_contents])
    inventory_selector.bind('<<ComboboxSelected>>', inventory_peek)
    
    global key_item_images
    key_item_images = []
    key_item_image_names = list_file_read(path.abspath(path.dirname(__file__)+"/Lists/Key_Item_Images"))
    for image in key_item_image_names:
        key_item_images.append(PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/Key_Items/"+image.rstrip())))
    
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
            kingdom_plans.append([flag, "Culinary Academy", PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/Kingdom_Plan/"+kingdom_plan_names[index]+".png")), check_flag(flag), kingdom_plan_placements[index]])
        else:
            kingdom_plans.append([flag, kingdom_plan_names[index], PhotoImage(file=path.abspath(path.dirname(__file__)+"/Images/Kingdom_Plan/"+kingdom_plan_names[index]+".png")), check_flag(flag), kingdom_plan_placements[index]])
        index+=1
    
    index = 0
    for plan in kingdom_plans:
        flip_plan = partial(flip_flag, plan[0])
        c = kingdom_plan_placements[0:index].count(plan[4])
        ttk.Checkbutton(tab_frames[plan[4]], image=plan[2], command=flip_plan, variable=plan[3]).grid(column=c%9, row=2+(2*(c//9)))
        ttk.Label(tab_frames[plan[4]], text=plan[1]).grid(column=c%9, row=1+(2*(c//9)))
        index += 1

def construct_counter_flag_menu():
    
    global root
    slot = 4
    gcf_top_menu_tab = root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
    counter_flags = keygen(path.abspath(path.dirname(__file__) + "/Tables/Counting_Flags"))
    entries = []
    labels = []
    vars = []
    partials = []
    separator = ttk.Notebook(gcf_top_menu_tab)
    tabs = [[ttk.Frame(separator), 1]]
    width = 6
    tab = 0
    c = 0
    flag = 1
    for i in range(len(counter_flags[0])):
        if int(flag) + 1 < int(counter_flags[0][i]):
            tabs.append([ttk.Frame(separator), counter_flags[0][i]])
            tab+=1
            c = 0
        flag = counter_flags[0][i]
        vars.append(IntVar(value=dolphin_memory_engine.read_byte(0x9041AC71 + int(flag))))
        partials.append(partial(set_cvar, [vars[i], flag]))
        entries.append(Entry(tabs[tab][0], textvariable=vars[i]))
        labels.append(ttk.Label(tabs[tab][0], text=counter_flags[1][i]))
        entries[i].grid(column=c%width, row=1+(2*(c//width)))
        labels[i].grid(column=c%width, row=2*(c//width))
        vars[i].trace_add('write', partials[i])
        c += 1

    for t in tabs:
        separator.add(t[0], text=t[1])
        
    separator.grid(column=0,row=0)
    
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
    flipper = partial(set_flag, flag, set)
    ttk.Button(bit_frame, text="Send!", command=flipper).grid(column=0, row=2)
    
    Label(counter_frame, text="Flag").grid(column=0, row=0)
    Label(counter_frame, text="Value").grid(column=1, row=0)
    
    cflag = IntVar(value=0)
    cset = IntVar(value=0)
    Entry(counter_frame, textvariable=cflag, width=3).grid(column=0, row=1)
    Entry(counter_frame, textvariable=cset, width=3).grid(column=1, row=1)
    csetter = partial(set_cvar, cflag, cset)
    ttk.Button(counter_frame, text="Send!", command=csetter).grid(column=0, row=2)


global root
root = Tk()
root.title("LKS Cheat Tool")
frm = ttk.Frame(root, padding=10)
frm.grid()

construct_top_menu()
construct_inventory_menu()
construct_kingdom_plan_menu()

disable_all(root)
lks_hook()

#construct_counter_flag_menu()
construct_debug_menu()

root.mainloop()

dolphin_memory_engine.un_hook()