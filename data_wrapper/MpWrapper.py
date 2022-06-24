# from mp_api import MPRester
import os

import pandas as pd
from pymatgen.ext.matproj import MPRester

from utils.log import logger


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
        all_prop = list(mpr.supported_properties)
        all_prop.append("full_formula")
        all_prop.append("structure")
        logger.info("Wrapping data on the Open Materials Project Database")
        try:

            data = list(mpr.query(query, all_prop))

            df = pd.DataFrame.from_dict(data)
            # df = self._featurizing_composition(df)
            df["source"] = "mp"
            return df

        except Exception as e:
            raise Exception(e)


if __name__ == "__main__":
    MP_API_KEY = os.environ.get("MP_API_KEY")
    mp = MpWrapper()
    q = "{Li,Na,K,Rb,Cs}-N"

    data = mp.wrap_mp(q, MP_API_KEY)
    print(data.head())
    print(data.columns.values)
