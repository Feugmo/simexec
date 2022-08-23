import time

from aiida import load_profile
from aiida.plugins import DataFactory
from db_query_builder import db_query
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sympy import det

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Energy Filter
@app.get("/get/filtered/energy/{e_min}/{e_max}")
def get_filter_energy(e_max: float, e_min: float):
    return db_query().energy_filter(e_min=e_min, e_max=e_max)


# Element Filter
@app.get("/get/filtered/element/{element}")
def filter_element(element: str):
    return db_query().element_filter(element=element)[0]


# Convex Hull Data
# @app.get("/get/filtered/element/{element}/count")
# def filter_element(element: str):
#     return db_query().element_filter(element=element)[1]


# Process Status Data
@app.get("/get/process")
def get_process():
    return db_query().fetch_process()[0]


# Process Num Data
@app.get("/get/process/num")
def get_process_num():
    return db_query().fetch_process()[1]


# Detailed Info for UUID
@app.get("/get/UUID/{calcu_node}")
def get_detailed_based_UUID(calcu_node: str):
    return db_query().UUID_Detailed_Info(calc_nodes=calcu_node)


@app.get("/get/UUID/cal_graph_pic/{cnode}")
async def get_img(cnode: str):
    db_query().process_plot_gen(cnode)
    time.sleep(2)
    img_path = f"graph/{cnode}.png"
    return FileResponse(img_path)
