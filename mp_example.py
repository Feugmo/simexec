import os

import pandas as pd
from mp_api import MPRester

MP_API_KEY = os.environ.get("MP_API_KEY")
print(MP_API_KEY)

MP_API_KEY = ""

mpr = MPRester(MP_API_KEY)
# print(mpr.materials.available_fields)


print(mpr.summary.available_fields)
# This is a helper function to shorten lists during the
# live presentation of this lesson for better readability.
# You can ignore it.
# def shortlist(long_list, n=5):
#     print("First {} of {} items:".format(min(n, 5), len(long_list)))
#     for item in long_list[0:n]:
#         print(item)
#
# with MPRester(MP_API_KEY) as mpr:
#     # You can pass in a formula to get_materials_ids
#     shortlist(mpr.get_materials_ids("LiFePO4"))
#     # Or you can pass in a "chemsys" such as "Li-Fe-P-O"
#     shortlist(mpr.get_materials_ids("Li-Fe-P-O"))
#
#
#
# with MPRester(MP_API_KEY ) as mpr:
#     structure = mpr.get_structure_by_material_id("mp-149")
#
#     # -- General search alternative:
#     doc = mpr.summary.get_data_by_id("mp-149", fields=["structure"])
#     structure = doc.structure
#
#
# # Here we query with the chemical system (chemsys)
#
#
#
#
#
# with MPRester(MP_API_KEY ) as mpr:
#     task_ids = mpr.get_task_ids_associated_with_material_id("mp-149")
#
#     # -- General search alternative:
#     doc = mpr.materials.get_data_by_id("mp-149", fields=["calc_types"])
#     task_ids = doc.calc_types.keys()
#     task_types = doc.calc_types.values()
#
#
# # Band gaps for all materials containing only Si and O
#
#
# with MPRester(MP_API_KEY ) as mpr:
#     docs = mpr.summary.search(chemsys="Si-O",
#                               fields=["material_id", "band_gap"])
#     mpid_bgap_dict = {doc.material_id: doc.band_gap for doc in docs}
#
# # Chemical formulas for all materials containing at least Si and O
#
# with MPRester(MP_API_KEY ) as mpr:
#     docs = mpr.summary.search(elements=["Si", "O"],
#                               fields=["material_id", "band_gap", "volume"])
#     mpid_formula_dict = {doc.material_id: doc.formula_pretty for doc in docs}
#

with MPRester(MP_API_KEY) as mpr:
    inputs = {"chemsys": "Mg-Al", "fields": ["material_id", "structure", "formation_energy_per_atom", "formula_pretty"]}
    docs = mpr.summary.search(**inputs)

    mpid_energy_dict = {doc.material_id: doc.formation_energy_per_atom for doc in docs}
    mpid_structure_dict = {doc.material_id: doc.structure for doc in docs}

example_doc = docs[0]

print("mpid", example_doc.material_id)  # a Materials Project ID
print("formula", example_doc.formula_pretty)  # a formula
print("formation_energy_per_atom", example_doc.formation_energy_per_atom)  # a volume

print("structure", example_doc.structure)

print(mpid_energy_dict)
