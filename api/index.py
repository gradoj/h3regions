import simplekml
import zipfile
import h3idx
import h3
from math import log
from io import BytesIO
from urllib.parse import urlparse, unquote
from http.server import BaseHTTPRequestHandler

colors={'Unknown':simplekml.Color.white,
        'EU868':simplekml.Color.yellow,
        'US915':simplekml.Color.blue,
        'CN779':simplekml.Color.red,
        'AU915':simplekml.Color.seagreen,
        'AU915-SB1':simplekml.Color.aquamarine,
        'CN470':simplekml.Color.red,
        'AS923-1':simplekml.Color.lawngreen,
        'AS923-1B':simplekml.Color.salmon,
        'AS923-1C':simplekml.Color.peachpuff,
        'AS923-2':simplekml.Color.lightgrey,
        'AS923-3':simplekml.Color.lightskyblue,
        'AS923-4':simplekml.Color.darkblue,
        'KR920':simplekml.Color.pink,
        'IN865':simplekml.Color.purple,
        'RU864':simplekml.Color.orange,
        'EU433':simplekml.Color.brown,
        'CD900-1A':simplekml.Color.beige}

def geth3(lat,lng,alt,hpo,vo):
    kml=simplekml.Kml(name='H3Regions')
    res=int(-1.044 * log(float(alt)) + 15.861)
    rings=int(26.097 * pow(float(alt),-0.17) )
    home_hex=h3.geo_to_h3(lat,lng,res)

    region_hex=h3idx.h3idx_get(home_hex,rings,res_offset=vo)
    
    num_hex=0
    for r in region_hex:
        for h in region_hex[r]:
            num_hex+=1
            gjhexhome=h3.h3_to_geo_boundary(h,geo_json=True)

            mpolyhome = kml.newmultigeometry(name=r)
            polhome=mpolyhome.newpolygon()
            polhome.extrude=True
            polhome.outerboundaryis=gjhexhome
            polhome.style.linestyle.width = 0.3
            #polhome.style.polystyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)
            if res < 2:
                polhome.style.linestyle.color = simplekml.Color.changealpha("50", colors[r] )
            else:
                polhome.style.linestyle.color = simplekml.Color.white
            polhome.style.polystyle.color = simplekml.Color.changealpha(str(hpo), colors[r])
            
    print('number of polygons: ', num_hex)
    #print(kml.kml())
    return kml.kml(format=False)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print('GET')
        self.send_response(200)
        #self.send_header('Content-type', 'text/plain')
        self.send_header('Content-type', 'application/vnd.google-earth.kmz')
        #self.send_header('Content-type', 'application/vnd.google-earth.kml+xml')
        self.end_headers()

        print(self.path)
        query = urlparse(self.path).query
        query=unquote(query)

        bbox,alt,hpo,vo=query.split(';')

        hpo = int(hpo.split('HPO=')[1])
        vo = int(vo.split('VO=')[1])
        # get the altitude of the camera
        alt = float(alt.split('CAMERA=')[1])
        west,south,east,north=bbox.split('BBOX=')[1].split(',')
    
        # find the center of the map and the altitude
        west = float(west)
        south = float(south)
        east = float(east)
        north = float(north)

        lng = ((east - west) / 2) + west
        lat = ((north - south) / 2) + south

        h3regions=geth3(lat=lat,lng=lng,alt=alt,hpo=hpo,vo=vo)

        in_memory_zip = BytesIO()

        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
        #zf = zipfile.ZipFile(in_memory_zip, "w")

        zf.writestr('h3regions.kml', h3regions)
        zf.close()   
        #print('after',len(in_memory_zip.getvalue()))
        self.wfile.write(in_memory_zip.getvalue())
        return

