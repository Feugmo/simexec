import os

# from constant import api_key, pass_word, profile
from aiida import load_profile

from data_wrapper import search_db

# from Convex_Hull import extract_db,  lammps_calculations, plot_convex_hull

MP_API_KEY = os.environ.get("MP_API_KEY")


query = {"chemsys": "Mg-Al", "fields": ["material_id", "structure", "formation_energy_per_atom", "formula_pretty"]}
docs = search_db.get_pd_db(query, "mp", key=MP_API_KEY)

mpid_energy_dict = {doc.material_id: doc.formation_energy_per_atom for doc in docs}
structures = [doc.structure for doc in docs]


print("formula:", structures[0].formula)

print("frac_coords:", structures[0].frac_coords)

print("lattice:", structures[0].lattice)


print("num_sites:", structures[0].num_sites)

print("species:", structures[0].species)

print("list_of_element:", [s.name for s in structures[0].species])

print("symbol_set:", structures[0].symbol_set)

print("atomic_numbers:", structures[0].atomic_numbers)

print("cart_coords:", structures[0].cart_coords)

print("composition:", structures[0].composition)

# load_profile()


# for structure in structures:
#     Sites = ''
#     cell = structures[0].lattice
#     result = lammps_calculations(sites=Sites, matrix=cell, codename="Lammps-optmize@localhost")
#     energys = []
#     for res in result:
#         energy = extract_db(result=res, database_name="material", user="lyuz11", port="5432", pass_word=pass_word)
#         energys.append(energy)
#     plot_convex_hull(element=Element, name=name, energy=energys)
