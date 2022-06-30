import os

# from constant import api_key, pass_word, profile
from aiida import load_profile

from Convex_Hull import lammps_calculations_v2
from data_wrapper import search_db

# from Convex_Hull import extract_db,  lammps_calculations, plot_convex_hull


# 1 Query the structure on MP using compoistion
MP_API_KEY = os.environ.get("MP_API_KEY")

query = {"chemsys": "Mg-Al", "fields": ["material_id", "structure", "formation_energy_per_atom", "formula_pretty"]}
docs = search_db.get_pd_db(query, "mp", key=MP_API_KEY)

mpid_energy_dict = {doc.material_id: doc.formation_energy_per_atom for doc in docs}
structures = [doc.structure for doc in docs]

# print("formula:", structures[0].formula)
#
# print("frac_coords:", structures[0].frac_coords)
#
# print("lattice:", structures[0].lattice)
#
# print("num_sites:", structures[0].num_sites)
#
# print("species:", structures[0].species)
#
# print("list_of_element:", [s.name for s in structures[0].species])
#
# print("symbol_set:", structures[0].symbol_set)
#
# print("atomic_numbers:", structures[0].atomic_numbers)
#
# print("cart_coords:", structures[0].cart_coords)
#
# print("composition:", structures[0].composition)

# 2  run calculaion on lammps using aiida

load_profile("lyuz11")

pass_word = os.environ.get("AIIDA_PASS_WORD")
user_name = os.environ.get("AIIDA_USER")
database_name = os.environ.get("AIIDA_DB")
for structure in structures:
    cell = []
    for x in structure.lattice.matrix:
        cell.append(list(x))
    position = structure.cart_coords
    composition = structure.composition
    element = [s.name for s in structure.species]
    result = lammps_calculations_v2(
        positions=position,
        elements=element,
        matrix=cell,
        codename="lammps.optimize@localhost",
        Potential_file="mg.liu.eam.alloy",
    )
    break
# plot_convex_hull(element="Mg-Al", name=name, energy=energys)

# main_data.energy_filter(e_min=-40,e_max=-20) #Energy filter

# 3 query the results on aiida database using  composition
from lammps.db_query import database_query

main_data = database_query(db_name="material", user=user_name, port="5432", pass_word=pass_word)
print(main_data.element_filter("Mg-Al"))  # filter for element
