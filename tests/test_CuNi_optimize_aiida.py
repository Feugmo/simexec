from aiida.common.extendeddicts import AttributeDict
from aiida.engine import run_get_node
from aiida.orm import Code, Dict, StructureData
from aiida.plugins import CalculationFactory
from aiida.engine import submit
import numpy as np
from ase.build import bulk
import matplotlib.pyplot as plt
from clusterx.parent_lattice import ParentLattice
from clusterx.structures_set import StructuresSet
from clusterx.super_cell import SuperCell

from aiida_lammps.data.potential import EmpiricalPotential

if __name__ == "__main__":

    from aiida import load_profile  # noqa: F401

    load_profile()

    codename = "lammps_optimize_graham@graham"

    ############################
    #  Define input parameters #
    ############################

    pri1 = bulk('Ni', 'fcc', cubic=False)
    sub1 = bulk('Cu', 'fcc', cubic=False)

    size = [4, 4, 4]
    nstruc = 1
    platt = ParentLattice(pri1, substitutions=[sub1])

    scell = SuperCell(platt, size)

    # lattice_param = prim[0].cell[0][0]
    sset = StructuresSet(platt)

    sub = {0: [1]}
    for _ in range(nstruc):
        sset.add_structure(scell.gen_random(sub))

    clx_structure = sset.get_structures()
    alloyAtoms = [structure.get_atoms() for structure in clx_structure]  # ASE Atoms Class

    symbols = alloyAtoms[0].get_chemical_symbols()
    positions = alloyAtoms[0].positions
    cell = alloyAtoms[0].cell

    # a =
    # b =
    # c =
    #
    # cell = [[a, 0, 0], [0, b, 0], [0, 0, c]]

    # cell = bulk('Ni').cell

    structure = StructureData(cell=cell)

    for i, position in enumerate(positions):
        structure.append_atom(
            position=position.tolist(), symbols=symbols[i]
        )

    structure.store()

    with open("CuNi.eam.alloy") as handle:
        eam_data = {"type": "alloy", "file_contents": handle.readlines()}

    potential = {"pair_style": "eam", "data": eam_data}

    # lammps_machine = {"num_machines": 1, "parallel_env": "mpi*", "tot_num_mpiprocs": 16}

    parameters_opt = {
        "units": "metal",
        "relax": {
            "type": "tri",  # iso/aniso/tri
            "pressure": 0.0,  # bars
            "vmax": 0.000001,  # Angstrom^3
        },
        "minimize": {
            "style": "cg",
            "energy_tolerance": 1.0e-25,  # eV
            "force_tolerance": 1.0e-25,  # eV angstrom
            "max_evaluations": 100000,
            "max_iterations": 50000,
        },
    }

    LammpsOptimizeCalculation = CalculationFactory("lammps.optimize")
    inputs = LammpsOptimizeCalculation.get_builder()

    # Computer options
    options = AttributeDict()
    options.account = ""
    options.qos = ""
    options.resources = {
        "num_machines": 1,
        "num_mpiprocs_per_machine": 1,
        "tot_num_mpiprocs": 1,
    }
    # options.queue_name = 'iqtc04.q'
    options.max_wallclock_seconds = 3600
    inputs.metadata.options = options

    # Setup code
    inputs.code = Code.get_from_string(codename)

    # setup nodes
    inputs.structure = structure
    inputs.potential = EmpiricalPotential(
        type=potential["pair_style"], data=potential["data"]
    )

    print(inputs.potential.get_potential_file())
    print(inputs.potential.atom_style)
    print(inputs.potential.default_units)

    inputs.parameters = Dict(dict=parameters_opt)

    # run calculation
    result, node = run_get_node(LammpsOptimizeCalculation, **inputs)
    print("results:", result)
    print("node:", node)

    # submit to deamon
    submit(LammpsOptimizeCalculation, **inputs)

