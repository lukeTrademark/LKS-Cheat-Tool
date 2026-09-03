# LKS Cheat Tool

LKS Cheat Tool is a program that hooks onto the Wii game Little King's Story and allows you to modify various elements of the game, without having to know exactly what bits and pieces of memory mean what things (and if you do, you could do even more!)

## Features

**General**: Edit your quantity of Bol, activate/deactivate a variety of key items and book entries, place arbitrary items inside your inventory, etc. You can even increase your inventory's capacity and use those new slots! (LKS only prepared for up to 100, though, and it also doesn't play nice when slots aren't filled sequentially...)  
**Game State**: Change your current chapter, what kings and guardians you have defeated, or set your castle level. Sometimes doesn't play as nice as you'd like, but a save and load can do wonders.
**Citizens**: Access the data about your citizens by internal ID or active presense in the Royal Guard and modify their position, name, job, etc.  
**Kingdom Plan**: Enable/Disable any kingdom plan at will, regardless of if it's even presently available to you.  
**Advanced**: Check/Flip any bit flag, check/alter any counting flag, or teleport Corobo via grid ID. Not very user friendly!  

## Questions/Issues

Q: Why does the inventory/hat/held item/equipment dropdown have all this other junk in it?  
A: So...the LKS devs were complete freaks, and made a ton of disparate objects use the exact same "Item" system, such as...well, spoils, hats, held items, and equipment on citizens. The visuals work with each other quite well too, so feel free to get silly with it! (the spoils and equipment are a ways down the list btw, type the name of one to jump the list to it)  

Q: Why is this check box/entry box greyed out?  
A: The check boxes are for things certainly important enough to add functionality for, but whose flags are currently unknown. Similar deal for entry boxes, except those are for values that don't play nice with being edited.  

Q: I'm trying to change a citizen's position, but the numbers keep fighting me!  
A: That's because the position data is updating live! Pause the game in Dolphin if you need an easier time moving people with your mind.  

Q: I'm on Mac! How can I use this?  
A: Uhh... Well, if you install the source code and dolphin-memory-engine, you can run it through the command line? (Just `python __init__.py`) If you install pyinstaller too, you could also build your own proper executable file. (`pyinstaller lks-cheat-tool.spec`)  

Q: It won't even freaking boot!!  
A: uuuuuuuuuugh i probably biffed something with the windows executable. *again.* that's a pretty urgent problem, so just, like, @ me in [the LKS discord server](https://discord.gg/t9chhfNYxB), my username's ιυκε™. if you have some other, less pressing, issue, then, like, make an issue. like the thing. from, github?  

## Special Thanks

**Bedrock_III** and **maythecatgirl**, for being the only other people in the LKS modding scene, and also often telling me where to even look for...just so much stuff.  
**toothpastedecay**, for being the first person in real life that I've met that knows what Little King's Story is. and for introducing me to the Discord and the fact that LKS actually has a community. And for humbling me in Smash.  
**Deadweight** (naturally), for being like the central force uniting people who love this beautiful game.  
And, **the general wider LKS community**, for fueling this autism so, so intensely.
