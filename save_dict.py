from pathlib import Path
import json
import os

def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


def h3idx_process():
    ''' read all region files and convert to python data structure
    
    '''
    filelist = Path(os.getcwd()).glob('data/*.h3idx')
    hex_dict={}
    for f in filelist:
        print('filename', f.name)
        filename=f.name
        region=filename[0:filename.find('.')]
        #print('region',region)

        file = open('data/'+filename, "rb")
        
        hexbytes = file.read(8) 
        while hexbytes:
            #print(hexbytes.hex())
            ba=bytearray(hexbytes)
            ba.reverse()
            region_hex=ba.hex()[1:] # remove the leading zero

            try:
                hex_dict[region].add(region_hex)
            except KeyError:
                hex_dict[region]=set()
                hex_dict[region].add(region_hex)
                continue
            
            hexbytes = file.read(8)
        file.close()
    #print(hex_dict)
    
    f = open("hex_dict.py", "w")
    f.write('hex_dict=')
    json.dump(hex_dict, f, default=serialize_sets)
    f.close()

    #return hex_dict



h3idx_process()