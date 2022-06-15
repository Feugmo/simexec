from ase import Atom, Atoms
from ase.build import bulk
from ase.calculators.lammpsrun import LAMMPS
import ase
from ase.build import bulk
import matplotlib.pyplot as plt
from ase.visualize.plot import plot_atoms

import os

# lmp_pot = '/home/tetsassic/Calculations/LAMMPS/potentials'
# potential = os.path.join(lmp_pot, "CuNi.eam.alloy")

# os.environ["ASE_LAMMPSRUN_COMMAND"] = ".venv/bin/mpirun -np 4 .venv/bin/lmp_mpi"

lmpcmd = ".venv/bin/mpirun -np 4 .venv/bin/lmp_mpi"


files = ['CuNi.eam.alloy']


structure = bulk('Cu', 'fcc', cubic=True) * [3, 3, 3]

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

lammps = LAMMPS(pair_style='eam/alloy', pair_coeff=['* * CuNi.eam.alloy Cu'], files=files, keep_tmp_files=True,
                verbose=True, )

structure.calc = lammps
print("Energy ", structure.get_potential_energy())
