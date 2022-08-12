# from Convex_Hull import extract_db,  lammps_calculations, plot_convex_hull
import os
from pathlib import Path

# from constant import api_key, pass_word, profile
from aiida import load_profile

from Convex_Hull import lammps_calculations_v2
from data_wrapper import search_db
from utils.log import logger

# 1 Query the structure on MP using compoistion
MP_API_KEY = os.environ.get("MP_API_KEY")

query = {"chemsys": "Mg-Al", "fields": ["material_id", "structure", "formation_energy_per_atom", "formula_pretty"]}
docs = search_db.get_pd_db(query, "mp", key=MP_API_KEY)

mpid_energy_dict = {doc.material_id: doc.formation_energy_per_atom for doc in docs}
structures = [doc.structure for doc in docs]

load_profile()

pass_word = os.environ.get("AIIDA_PASS_WORD")
user_name = os.environ.get("AIIDA_USER")
database_name = os.environ.get("AIIDA_DB")


print(pass_word, user_name, database_name)
pot_file = os.path.join(Path(__file__).parent, "lammps/potentials/almg.liu.eam.alloy")
try:
    assert os.path.isfile(pot_file)
    logger.info(f" Found potenfial file : [{pot_file}]")
except AssertionError:
    logger.error(f" No such file: [{pot_file}]")
for structure in structures:
    cell = []
    for x in structure.lattice.matrix:
        cell.append(list(x))
    position = structure.cart_coords
    composition = structure.composition
    element = [s.name for s in structure.species]
    result = lammps_calculations_v2(
        positions=position, elements=element, matrix=cell, codename="lammps.optimize@localhost", Potential_file=pot_file
    )
    break
# plot_convex_hull(element="Mg-Al", name=name, energy=energys)

# main_data.energy_filter(e_min=-40,e_max=-20) #Energy filter

# 3 query the results on aiida database using  composition
from lammps.db_query import database_query

main_data = database_query(db_name="material", user=user_name, port="5432", pass_word=pass_word)
print(main_data.element_filter("Mg-Al"))  # filter for element
