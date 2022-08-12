# from aiida import load_profile
# from constant import api_key, pass_word, profile
# from Convex_Hull import extract_db, get_DFT_ene, get_structure_data, lammps_calculations, plot_convex_hull
#
# Element = "Mg-Al"
# DFT_Value = get_DFT_ene(api_key=api_key, Element=Element)
# id = DFT_Value["MP ID"]
# DFT_energy = DFT_Value["energy"]
# name = DFT_Value["name"]
#
# structure = get_structure_data(api_key=api_key, id=id)
# Sites = structure["Sites"]
# cell = structure["Matrix"]
# load_profile(profile)
# result = lammps_calculations(sites=Sites, matrix=cell, codename="Lammps-optmize@localhost")
# energys = []
# for res in result:
#     energy = extract_db(result=res, database_name="material", user="lyuz11", port="5432", pass_word=pass_word)
#     energys.append(energy)
# plot_convex_hull(element=Element, name=name, energy=energys)
