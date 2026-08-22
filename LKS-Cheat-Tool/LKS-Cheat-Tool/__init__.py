from file_readers import *
from element_creators import *
from memory_modifiers import *
import cfg

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
    
    hooked = False
    
    dolphin_memory_engine.hook()
    
    if (dolphin_memory_engine.is_hooked()):
        if (dolphin_memory_engine.read_bytes(0x80000000, 6) == b"RO3EXJ") | (dolphin_memory_engine.read_bytes(0x80000000, 6) == b"RO3P99"):
            hooked = True
    
    if not(hooked):
        dolphin_memory_engine.un_hook()
        cfg.root.after(1000, lks_hook)
    else:
        enable_all(cfg.root)
        
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

def wait_for_hook():
    
    if len(cfg.root.winfo_children()) == 1:
        loading_frame = ttk.Frame(cfg.root)
        loading_frame.grid(column=0, row=0)
        Label(loading_frame, text="Waiting for LKS...").grid(column=0, row=0)
        bar = ttk.Progressbar(loading_frame, mode='indeterminate', length=200)
        bar.grid(column=1, row=0)
        bar.start(15)
        
    if dolphin_memory_engine.is_hooked():
        cfg.root.winfo_children()[1].destroy()
        construct_inventory_menu()
        construct_gamestate_menu()
        construct_citizens_menu()
        construct_kingdom_plan_menu()
        construct_debug_menu()
    else:
        cfg.root.after(1000, wait_for_hook)

def construct_top_menu():
    
    frame = cfg.root.winfo_children()[0]
    
    top_menu = ttk.Notebook(frame)
    top_menu.grid(column=0, row=2)
    top_menu_tabs=[[ttk.Frame(top_menu), "General"], [ttk.Frame(top_menu), "Game State"], [ttk.Frame(top_menu), "Citizens"], [ttk.Frame(top_menu), "Kingdom Plans"], [ttk.Frame(top_menu), "Advanced"]]
    for tab in top_menu_tabs:
        top_menu.add(tab[0], text=tab[1])
        
def construct_inventory_menu():
    
    slot = 1
    inv_top_menu_tab = cfg.root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
    ttk.Label(inv_top_menu_tab, text="Bol Count").grid(column=0, row=0, sticky='es')
    create_live_entry(inv_top_menu_tab, "word", 0x9041B350).grid(column=1, row=0, sticky='sw')
    ttk.Label(inv_top_menu_tab, text="Inventory Size").grid(column=3, row=0, sticky='es')
    create_live_entry(inv_top_menu_tab, "word", 0x9041B34A).grid(column=4, row=0, sticky='sw')
    
    ttk.Separator(inv_top_menu_tab, orient='horizontal').grid(column=0, row=1, columnspan=5, sticky='esw')
    
    ttk.Label(inv_top_menu_tab, text="Arrow Count").grid(column=0, row=2, sticky='es')
    create_live_entry(inv_top_menu_tab, "word", 0x92283370, ['readonly']).grid(column=1, row=2, sticky='sw')
    ttk.Label(inv_top_menu_tab, text="Brainy Doctor Doses").grid(column=0, row=3, sticky='e')
    create_live_entry(inv_top_menu_tab, "word", 0x92283388, ['readonly']).grid(column=1, row=3, sticky='w')
    ttk.Label(inv_top_menu_tab, text="Rainbow Wizard Spell Slots").grid(column=0, row=4, sticky='ne')
    create_live_entry(inv_top_menu_tab, "word", 0x9228337C, ['readonly']).grid(column=1, row=4, sticky='nw')
    
    ttk.Separator(inv_top_menu_tab, orient='vertical').grid(column=2, row=2, rowspan=3, sticky='ns')
    
    ttk.Label(inv_top_menu_tab, text="HP Modifier").grid(column=3, row=2, sticky='es')
    create_live_entry(inv_top_menu_tab, "word", 0x9041BACC).grid(column=4, row=2, sticky='sw')
    ttk.Label(inv_top_menu_tab, text="Attack Modifier").grid(column=3, row=3, sticky='e')
    create_live_entry(inv_top_menu_tab, "word", 0x9041BAD0).grid(column=4, row=3, sticky='w')
    
    ttk.Separator(inv_top_menu_tab, orient='horizontal').grid(column=0, row=5, columnspan=5, sticky='new')
    
    ttk.Label(inv_top_menu_tab, text="Day Count").grid(column=0, row=6, sticky='ne')
    create_live_entry(inv_top_menu_tab, "word", 0x903E8904).grid(column=1, row=6, sticky='nw')
    ttk.Label(inv_top_menu_tab, text="Time").grid(column=3, row=6, sticky='ne')
    create_live_entry(inv_top_menu_tab, "float", 0x903E8908).grid(column=4, row=6, sticky='nw')
    
    standard_inventory = ttk.Labelframe(inv_top_menu_tab, text="Inventory")
    standard_inventory.grid(column=5, row=0, rowspan=7)
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
    key_item_notebook.grid(column=0, row=7, columnspan=6)
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
    entries = [[489, "Onii King"], [490, "Duvroc"], [491, "Shishkebaboo"], [492, "Omelet"], [493, "TV Dinnah"], [494, "Long Sauvage"], [495, "Jumbo Champloon"], [32030, "Onii King"], [32031, "Duvroc"], [32032, "Shishkebaboo"], [32033, "Omelet"], [32034, "TV Dinnah"], [32035, "Long Sauvage"], [32036, "Jumbo Champloon"]]
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
            create_flag_box(int(entries[0][i]), bools[0], curr_frame, name, image).grid(column=3, row=3, columnspan=2, sticky='n')
        if (i != 0) & (i < 5):
            Label(curr_frame, text=name).grid(column=i, row=0)
            create_flag_box(int(entries[0][i]), bools[0], curr_frame, name, image).grid(column=i, row=1, sticky='n')
        if (i > 4) & (i != 7):
            Label(curr_frame, text=name).grid(column=i-4, row=2)
            create_flag_box(int(entries[0][i]), bools[0], curr_frame, name, image).grid(column=i-4, row=3, sticky='n')
    
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

    books = [[3, "/Tables/Wonder_Spots", (0x9041e71a * 8) + 1, "Wonder_Spots", 10], [4, "/Tables/UMA_Logs", (0x9041bf50 * 8), "UMA_Pages", 12], [5, "/Tables/Gourmet_Entries", 0, "Gourmet_Pages", 10], [6, "/Tables/Animals", (0x9041e76a * 8) + 1, "Animal_Entries", 7], [7, "/Tables/Hums", (0x9041e73a * 8) + 1, "Hum_Pages", 10], [8, "/Tables/Kingstones", (0x9041e75a * 8) + 1, "Kingstones", 7], [10, "/Tables/Cutscenes", (0x9041e72a * 8) + 1, "Cutscene_Thumbnails", 9]]
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

def construct_gamestate_menu():
    
    slot = 2
    gs_top_menu_tab = cfg.root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
    chapter_window = ttk.Labelframe(gs_top_menu_tab, text="Chapter Select")
    chapter_window.grid(column=0, row=0, columnspan=2, rowspan=4)
    name_list = ["Chapter 1: Prologue (Unused)", "Chapter 2: Tutorial", "Chapter 3: Onii King", "Chapter 4: Sunflower Plains", "Chapter 5: Skull Plains", "Chapter 6: World of God"]
    for i in list(range(6)):
        ttk.Radiobutton(chapter_window, text=name_list[i], variable=cfg.curr_chapter, value=i+1).grid(column=0, row=i, sticky='w')
    get_chapter()
    cfg.curr_chapter.trace_add('write', partial(set_chapter, cfg.curr_chapter))
    
    king_window = ttk.Labelframe(gs_top_menu_tab, text="Kings Defeated")
    king_window.grid(column=2, row=0, columnspan=1, rowspan=4)
    king_list = ["Onii King", "King Duvroc", "King Shishkebaboo", "King Omelet", "King TV Dinnah", "King Long Sauvage", "King Jumbo Champloon"]
    king_kill_flags = [[2048], [2304, 2313], [2305, 2314], [2561, 2565, 2566], [2562], [2564], [2563]]
    for i in list(range(7)):
        create_flag_box(king_kill_flags[i], BooleanVar(), king_window, king_list[i]).grid(column=0, row=i)

    guardian_window = ttk.Labelframe(gs_top_menu_tab, text="Guardians Defeated")
    guardian_window.grid(column=3, row=0, columnspan=1, rowspan=4)
    guardian_list = ["Cow Bones", "Onii Man", "Yvonne", "Mush Bro", "Mush Geezer", "Clockwork Knight", "Owl Hag", "Ogre Ergo", "Radeeze", "Blue Dragon"]
    guardian_kill_flags = [[840, 1819], [841, -1], [842, 1214, 1224], [844, 1229], [845, 1230], [843, 1225], [846, 1226], [847, 1227], [848, 1228], [849, 1231, 1232]]
    for i in list(range(10)):
        create_flag_box(guardian_kill_flags[i], BooleanVar(), guardian_window, guardian_list[i]).grid(column=0, row=i)

def construct_citizens_menu():
    
    slot = 3
    citizens_top_menu_tab = cfg.root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
    index = 24
    while (dolphin_memory_engine.read_word(get_save_pos(0x903F6B20 + (452 * index))) != 0):
        offset = 0x903F6B20 + (452 * index)
        index+=1
    
    ttk.Label(citizens_top_menu_tab, text="Citizen Number").grid(column=0, row=0, sticky='es')
    selected_slot = StringVar()
    citizen_selector = ttk.Combobox(citizens_top_menu_tab, textvariable=selected_slot)
    citizen_selector['values'] = tuple(range(index))
    citizen_selector.grid(column=1, row=0, sticky='sw')
    citizen_readout = ttk.Labelframe(citizens_top_menu_tab, text="Selected")
    citizen_readout.grid(column=0, row=1, columnspan=2, sticky='n')
    name_key = list_file_read(path.abspath(path.dirname(__file__)+"/Lists/Names"))
    job_key = keygen(path.abspath(path.dirname(__file__)+"/Tables/Job_IDs"))
    item_key = keygen(path.abspath(path.dirname(__file__)+"/Tables/Items"))
    citizen_peek = partial(view_citizen, citizen_readout, selected_slot, name_key, job_key, item_key, 'full')
    citizen_selector.bind('<<ComboboxSelected>>', citizen_peek)
    
    rg_section = ttk.Labelframe(citizens_top_menu_tab, text="Royal Guard")
    rg_section.grid(column=2, row=0, rowspan=5)
    Label(rg_section, text="Royal Guard Cap").grid(column=0, row=0, sticky='e')
    rg_max = IntVar()
    Entry(rg_section, textvariable=rg_max).grid(column=1, row=0, sticky='w')
    rg_max.trace_add('write', partial(set_cvar, IntVar(value=41), rg_max))
    update_loop('byte', 0x9041AC9A, rg_max)
    rg_scroll_frame = create_scroll_frame(rg_section, 0, 1, 750, 420, 3)
    rg_subframes = []
    chartypes = []
    partials = []
    for index in list(range(30)):
        rg_subframes.append(ttk.Labelframe(rg_scroll_frame, text = "Slot " + str(index+1)))
        slot = 0x92BC4310 + (index * 1736)
        chartypes.append(IntVar(value=0))
        partials.append(partial(find_and_build_citizen, chartypes[index], rg_subframes[index], name_key, job_key, item_key))
        chartypes[index].trace_add('write', partials[index])
        update_loop("word", slot+648, chartypes[index])
        rg_subframes[index].grid(column=index%3, row=1+(index//3))

def construct_kingdom_plan_menu():
    
    slot = 4
    kp_top_menu_tab = cfg.root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
   
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
    
    slot = 5
    debug_top_menu_tab = cfg.root.winfo_children()[0].winfo_children()[0].winfo_children()[slot-1]
    
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
    
    construction_frame = ttk.Labelframe(debug_top_menu_tab, text="Building Status")
    construction_frame.grid(column=3, row=0)
    
    cons_selector = IntVar()
    cons_mode = StringVar()
    ttk.Spinbox(construction_frame, from_=0, to=206, textvariable=cons_selector, width=3).grid(column=0, row=0)
    ttk.Radiobutton(construction_frame, text="Inactive", variable=cons_mode, value="inactive").grid(column=1, row=0)
    ttk.Radiobutton(construction_frame, text="Sign", variable=cons_mode, value="sign").grid(column=2, row=0)
    ttk.Radiobutton(construction_frame, text="Built", variable=cons_mode, value="built").grid(column=3, row=0)
    cons_selector.trace_add("write", partial(get_building, cons_selector, cons_mode))
    ttk.Button(construction_frame, text="Send!", command=partial(set_building, cons_selector, cons_mode)).grid(column=1, row=1, columnspan=3)

ver_num = "0.7.0_dev"
cfg.root.title("LKS Cheat Tool v" + ver_num)
frm = ttk.Frame(cfg.root, padding=10)
frm.grid()

construct_top_menu()

disable_all(cfg.root)
wait_for_hook()
lks_hook()

cfg.root.mainloop()

dolphin_memory_engine.un_hook()