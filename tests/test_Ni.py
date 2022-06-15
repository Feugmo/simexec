from ase import Atom, Atoms
from ase.build import bulk
from ase.calculators.lammpsrun import LAMMPS
import ase
from ase.build import bulk
import matplotlib.pyplot as plt
from clusterx.parent_lattice import ParentLattice
from clusterx.structures_set import StructuresSet
from clusterx.super_cell import SuperCell
from clusterx.visualization import juview
from clusterx.super_cell import SuperCell
import numpy as np
from ase.visualize.plot import plot_atoms

import os

# lmp_pot = '/home/tetsassic/Calculations/LAMMPS/potentials'
# potential = os.path.join(lmp_pot, "CuNi.eam.alloy")

os.environ["ASE_LAMMPSRUN_COMMAND"]= "/home/tetsassic/anaconda3/envs/aiida/bin/mpirun -np 4 /home/tetsassic/anaconda3/envs/aiida/bin/lmp_mpi"



lmpcmd = "/home/tetsassic/anaconda3/envs/aiida/bin/mpirun -np 4 /home/tetsassic/anaconda3/envs/aiida/bin/lmp_mpi"

# lmpcmd="/home/tetsassic/anaconda3/envs/aiida/bin/lmp_mpi"

files = ['library.meam', 'Ni.meam']

# parameters = {'pair_style': 'eam/alloy',
#               'pair_coeff': ['* * CuNi.eam.alloy Ni Cu'],
#               'command': lmpcmd,
#               }

# pri1 = bulk('Ni', 'fcc', cubic=True)
# sub1 = bulk('Cu', 'fcc', cubic=True)
#
# size = [4, 4, 4]
# nstruc = 1
# platt = ParentLattice(pri1, substitutions=[sub1])
#
# scell = SuperCell(platt, size)

# lattice_param = prim[0].cell[0][0]
# sset = StructuresSet(platt)
#
# sub = {0: [1]}
# for _ in range(nstruc):
#     sset.add_structure(scell.gen_random(sub))
#
# clx_structure = sset.get_structures()
# alloyAtoms = [structure.get_atoms() for structure in clx_structure]  # ASE Atoms Class
#
# structure = alloyAtoms[0]

structure = bulk('Ni', 'fcc', cubic=True)* [3,3,3]


fig, ax = plt.subplots(1, 3)

ase.visualize.plot.plot_atoms(
    structure,
    ax[0],
    radii=0.8,
    # rotation=("0x, 0y, 0z") # uncomment to visualize at different angles
)
ase.visualize.plot.plot_atoms(
    structure,
    ax[1],
    radii=0.8,
    rotation=("0x, 45y, 45z")  # uncomment to visualize at different angles
)
ase.visualize.plot.plot_atoms(
    structure,
    ax[2],
    radii=0.8,
    rotation=("-45x, -45y, 0z"),  # uncomment to visualize at different angles
)

plt.show()

print(structure.get_chemical_formula())

# lammps = LAMMPS(tmp_dir='/home/tetsassic/lammps_tmp/CuNi', parameters=parameters, files=files)

lammps = LAMMPS(pair_style='meam', pair_coeff=['* * library.meam Ni  Ni.meam Ni'],  files=files,  keep_tmp_files=True,verbose=True)

structure.calc = lammps
print("Energy ", structure.get_potential_energy())
