import fileinput
from fileinput import FileInput
from os import path
from os import listdir

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

def list_file_read(filename):
    
    output = []
    file = fileinput.input(files=filename)
    for line in file:
        output.append(line.rstrip())
        
    return output

def read_table(table, key):
    
    key_set = table[0]
    output_set = table[1]
    
    if (key_set.count(key)) > 0:
        result = output_set[key_set.index(key)]
    else:
        result = "Not Found"
    
    return result