import os

# from pymatgen.ext.matproj import MPRester
# from mp_api import MPRester
from mp_api.matproj import MPRester

from utils.log import logger

# import pandas as pd


class MpWrapper:
    """
    wrap data on Materials project
    adapted from https://workshop.materialsproject.org/lessons/04_materials_api/api_use/
    """

    def __init__(
        self,
    ):
        pass

    def wrap_mp(self, query, MP_API_KEY):
        """
        mpr.query('{Li,Na,K,Rb,Cs}-N', ['material_id', 'pretty_formula'])
        :param query:
        :return: dataframe
        """

        mpr = MPRester(MP_API_KEY)

        # available_fields = mpr.summary.available_fields

        # all_prop = list(mpr.supported_properties)
        # all_prop.append("full_formula")
        # all_prop.append("structure")
        logger.info("Wrapping data on the Open Materials Project Database")
        try:

            # data = list(mpr.query(query, all_prop))

            datas = mpr.summary.search(**query)

            # df = pd.DataFrame.from_dict(data)
            # df = self._featurizing_composition(df)
            # df["source"] = "mp"
            return datas

        except Exception as e:
            raise Exception(e)


if __name__ == "__main__":
    MP_API_KEY = os.environ.get("MP_API_KEY")

    with MPRester(MP_API_KEY) as mpr:
        inputs = {
            "chemsys": "Mg-Al",
            "fields": ["material_id", "structure", "formation_energy_per_atom", "formula_pretty"],
        }
        docs = mpr.summary.search(**inputs)

        mpid_energy_dict = {doc.material_id: doc.formation_energy_per_atom for doc in docs}
        mpid_structure_dict = {doc.material_id: doc.structure for doc in docs}

    example_doc = docs[0]

    print("mpid", example_doc.material_id)  # a Materials Project ID
    print("formula", example_doc.formula_pretty)  # a formula
    print("formation_energy_per_atom", example_doc.formation_energy_per_atom)  # a volume
