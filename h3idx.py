import os
import h3
from pathlib import Path

def h3idx_get(h3hex, rings, res_offset=5):
    ''' pass in h3 hex and number of rings around hex at same resolution to check if h3idx hexes are present
        input:  h3hex 
                rings - number of rings around h3hex to check
                res_offset - used to drop high resolution hexes at high altitudes
        output: list of h3hexes present in h3idx files
    '''

    res=h3.h3_get_resolution(h3hex)
    filelist = Path(os.getcwd()).glob('data/*.h3idx')

    # generate the larger hex rings centered around the cameras center of view
    # use 7 hex here as h3idx files use 7 as a maximum resolution
    
    view_hex={}
    view_hex[res]=h3.k_ring(h3hex,rings)

    # fill up a dictionary of hexes of the our current view
    for i in range(0,8): 
        if i != res:
            view_hex[i]=set()
        for h in view_hex[res]:
            if i < res:
                view_hex[i].add(h3.h3_to_parent(h,i)) 
            else:
                view_hex[i].update(h3.h3_to_children(h,i))

    #print(view_hex)
    common_hex={}
    
    idx_hex=[]
    hex_dict={}
    for f in filelist:
        #print('filename', f.name)
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

            # check if resolution is too high to display at this altitude
            if h3.h3_get_resolution(region_hex) > (res+res_offset):
                pass
            elif region_hex in view_hex[h3.h3_get_resolution(region_hex)]:

                try:
                    hex_dict[region].add(region_hex)
                except KeyError:
                    hex_dict[region]=set()
                    hex_dict[region].add(region_hex)
                    continue
            
            hexbytes = file.read(8)
        file.close()
    #print(hex_dict)
    return hex_dict



if __name__ == '__main__':
    h3idx_get('87281bb70ffffff', 2)