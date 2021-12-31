import h3
import json
from time import time

try:
    from hex_dict import hex_dict
except:
    import save_dict
    from hex_dict import hex_dict

def h3idx_get(h3hex, rings, res_offset=5):
    ''' pass in h3 hex and number of rings around hex at same resolution to check if h3idx hexes are present
        input:  h3hex 
                rings - number of rings around h3hex to check
                res_offset - used to drop high resolution hexes at high altitudes
        output: list of h3hexes present in h3idx files
    '''
    global hex_dict
    res=h3.h3_get_resolution(h3hex)

    # generate the larger hex rings centered around the cameras center of view
    # use 7 hex here as h3idx files use 7 as a maximum resolution
    
    start=time()
    view_hex={}
    view_hex[res]=h3.k_ring(h3hex,rings)
    # fill up a dictionary of hexes of the our current view
    for i in range(0,res+res_offset+1): 
        if i != res:
            view_hex[i]=set()
        for h in view_hex[res]:
            if i < res:
                view_hex[i].add(h3.h3_to_parent(h,i)) 
            else:
                view_hex[i].update(h3.h3_to_children(h,i))
    end = time()
    print(f'It took {end - start} seconds to create the hex view set')

    #print(view_hex)
    start = time()
    idx_dict={}
    for region in hex_dict:
        #print('region',region)
        for region_hex in hex_dict[region]:

            # check if resolution is too high to display at this altitude
            if h3.h3_get_resolution(region_hex) > (res+res_offset):
                pass
            elif region_hex in view_hex[h3.h3_get_resolution(region_hex)]:

                try:
                    idx_dict[region].add(region_hex)
                except KeyError:
                    idx_dict[region]=set()
                    idx_dict[region].add(region_hex)
                    continue
    end = time()
    print(f'It took {end - start} seconds to find region hex that match view hex')
    return idx_dict



if __name__ == '__main__':

    h3idx_get('87281bb70ffffff', 2)
