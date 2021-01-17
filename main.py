import os
from pathlib import Path

from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from openrouteservice import client
from openrouteservice.geocode import pelias_search as geocode

OPENROUTESERVICE_TOKEN = os.environ['OPENROUTESERVICE_TOKEN']
DGT_URL = 'http://infocar.dgt.es/etraffic/BuscarElementos?latNS=44&longNS=5&latSW=27&longSW=-19&zoom=6&accion=getElementos&Camaras=true&SensoresTrafico=true&SensoresMeteorologico=true&Paneles=true&Radares=true&IncidenciasRETENCION=true&IncidenciasOBRAS=false&IncidenciasMETEOROLOGICA=true&IncidenciasPUERTOS=true&IncidenciasOTROS=true&IncidenciasEVENTOS=true&IncidenciasRESTRICCIONES=true&niveles=true&caracter=acontecimiento';


openroute = client.Client(key=OPENROUTESERVICE_TOKEN)
app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)

templates = Jinja2Templates(directory="templates")
"""
#with open('index.html') as fname:
#    index_html_content = fname.read()
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=index_html_content, status_code=200)

"""

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )

@app.get("/events")
async def get_dgt_events():
    return httpx.get(DGT_URL).json()


def geo(geo_text):
    return geocode(openroute, geo_text)['features'][0]['geometry']['coordinates']  

@app.get("/geo")
async def get_geo(geo_text):
    return geo(geo_text)


@app.get("/route")
async def get_route(origin_text, destination_text):
    origin = geo(origin_text)
    destination = geo(destination_text)
    request_params = {'coordinates': [origin, destination],
                'format_out': 'geojson',
                'profile': 'driving-car',
                'preference': 'shortest',
                'instructions': 'false',}
    route = openroute.directions(**request_params)
    return route
