import os

import yaml

# from constant import api_key, pass_word, profile
from aiida import load_profile

from data_wrapper import search_db

# from Convex_Hull import extract_db, get_DFT_ene, get_structure_data, lammps_calculations, plot_convex_hull


# ============================ Create Chemical space =====================================


# TODO
# 1- wrap data online  material project, open quantum, nomad

# with open(os.path.join(workdir, 'configuration/Query.yml')) as fr:
#     Query = yaml.safe_load(fr)


# MP_API_KEY = os.environ.get("MP_API_KEY_LEGACY")

MP_API_KEY = ""
print("****", MP_API_KEY)

Query = {"criteria": "{Mg}-Al"}
data = search_db.get_pd_db(Query["criteria"], "mp", key=MP_API_KEY)

print(data.columns)

print(data.head())

for index, row in data.iterrows():
    print(row["full_formula"])

structures = [row["structure"] for _, row in data.iterrows()]


print("formula:", structures[0].formula)

print("frac_coords:", structures[0].frac_coords)

print("lattice:", structures[0].lattice)

# print('positions:', structures[0].pos)

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
