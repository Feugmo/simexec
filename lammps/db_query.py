import collections
import math

import psycopg2.extras
from psycopg2 import sql


def db_query_element(database_name, user, port, pass_word, element_query, e_min, e_max):
    """
    Input:
    database_name: The name of your database
    user: User name for database
    port: port access to database
    pass_word: user password
    element_query: element you want query inside the database example"Al-Mg"
    e_min/e_max: can be None (if None then emin/emax will be set to -+inf), you can enter the energy range to further filter the result
    output:
    Dictionary contains the formula, cells, sites and energy
    """
    result = {}
    energys = []
    structures = []
    cells = []
    sites_info = []
    conn = psycopg2.connect(dbname=database_name, user=user, password=pass_word, host="127.0.0.1", port=port)
    cur = conn.cursor()
    cur.execute(
        """
    SELECT attributes,id FROM db_dbnode
    WHERE node_type='data.core.structure.StructureData.'
    """
    )
    element_type = cur.fetchall()
    element = element_query
    elements = element.split("-")
    for j in element_type:
        system = []
        for i in j[0]["kinds"]:
            system.append(i["symbols"][0])
        if set(elements).issubset(system):
            cur.execute(
                """
            SELECT output_id FROM db_dblink
            WHERE input_id={}
            """.format(
                    j[1]
                )
            )
            out_id = cur.fetchall()
            if len(out_id) > 0:
                cur.execute(
                    """
                    SELECT attributes FROM  db_dbnode
                    WHERE id = {}
                    """.format(
                        out_id[1][0] - 1
                    )
                )
                energy = cur.fetchall()[0][0]["energy"]
                if e_min is None and e_max is None:
                    e_min = -math.inf
                    e_max = math.inf

                elif e_min is None:
                    e_min = e_max - 10
                elif e_max is None:
                    e_max = e_min + 10

                if energy > e_min and energy < e_max:
                    energys.append(energy)
                    cells.append(j[0]["cell"])
                    symb = []
                    for ii in j[0]["sites"]:
                        symb.append(ii["kind_name"])
                    formula = collections.Counter(symb)
                    structures.append(formula)
                    sites_info.append(j[0]["sites"])

    result["Formula"] = structures
    result["Cell"] = cells
    result["Sites"] = sites_info
    result["Energy"] = energys

    cur.close()
    conn.close()
    return result


def db_query_energy(database_name, user, port, pass_word, e_min, e_max, element):
    """
    Input:
    database_name: The name of your database
    user: User name for database
    port: port access to database
    pass_word: user password
    e_min/e_max: can be None,(if None then emin/emax will be set to -+inf) you can enter the energy range to further filter the result
    element: Can be none, you can put element name to filter the result example"Mg-Al"
    """
    result = {}
    if element is not None:
        elements = element.split("-")
    energys = []
    structures = []
    cells = []
    sites_info = []
    conn = psycopg2.connect(dbname=database_name, user=user, password=pass_word, host="127.0.0.1", port=port)
    cur = conn.cursor()
    cur.execute(
        """
    SELECT output_id FROM db_dblink
    WHERE label='results'
    """
    )
    energy_id = cur.fetchall()
    for e_id in energy_id:
        cur.execute(
            """
        SELECT attributes FROM db_dbnode
        WHERE id={}
        """.format(
                e_id[0]
            )
        )
        e_query = cur.fetchall()[0][0]["energy"]
        if e_min is None and e_max is None:
            e_min = -math.inf
            e_max = math.inf

        elif e_min is None:
            e_min = e_max - 10
        elif e_max is None:
            e_max = e_min + 10
        if e_query > e_min and e_query < e_max:
            cur.execute(
                """
            SELECT input_id FROM db_dblink
            WHERE output_id={} AND label='structure'
            """.format(
                    e_id[0] + 1
                )
            )
            str_id = cur.fetchall()[0][0]
            cur.execute(
                """
            SELECT attributes FROM db_dbnode
            WHERE id={}
            """.format(
                    str_id
                )
            )
            structure_data = cur.fetchall()[0][0]
            if elements is None:
                symb = []
                for ii in structure_data["sites"]:
                    symb.append(ii["kind_name"])
                formula = collections.Counter(symb)
                energys.append(e_query)
                structures.append(formula)
                cells.append(structure_data["cell"])
                sites_info.append(structure_data["sites"])
            else:
                system = []
                for i in structure_data["kinds"]:
                    system.append(i["symbols"][0])
                if set(elements).issubset(system):
                    symb = []
                    for ii in structure_data["sites"]:
                        symb.append(ii["kind_name"])
                    formula = collections.Counter(symb)
                    energys.append(e_query)
                    structures.append(formula)
                    cells.append(structure_data["cell"])
                    sites_info.append(structure_data["sites"])
                else:
                    pass
    result["Formula"] = structures
    result["Cell"] = cells
    result["Sites"] = sites_info
    result["Energy"] = energys
    cur.close()
    conn.close()

    return result


class database_query:
    def __init__(self, db_name, user, port, pass_word):
        self.db_name = db_name
        self.user = user
        self.port = port
        self.pass_word = pass_word

    def get_data(self):
        result = {}
        energys = []
        structures = []
        eles = []
        cells = []
        dbn = self.db_name
        user = self.user
        port = self.port
        pw = self.pass_word
        conn = psycopg2.connect(dbname=dbn, user=user, password=pw, host="127.0.0.1", port=port)
        cur = conn.cursor()
        cur.execute(
            """
        SELECT output_id FROM db_dblink
        WHERE label='results'
        """
        )
        energy_id = cur.fetchall()
        for e_id in energy_id:
            cur.execute(
                """
            SELECT attributes FROM db_dbnode
            WHERE id={}
            """.format(
                    e_id[0]
                )
            )
            energy = cur.fetchall()[0][0]["energy"]
            cur.execute(
                """
                SELECT input_id FROM db_dblink
                WHERE output_id={} AND label='structure'
                """.format(
                    e_id[0] + 1
                )
            )
            structure_id = cur.fetchall()[0][0]
            cur.execute(
                """
            SELECT attributes FROM db_dbnode
            WHERE id={}
            """.format(
                    structure_id
                )
            )
            structure_info = cur.fetchall()[0][0]
            energys.append(energy)
            structures.append(structure_info["sites"])
            cells.append(structure_info["cell"])
            eles.append(structure_info["kinds"])
        result["Elements"] = eles
        result["Energy"] = energys
        result["Cells"] = cells
        result["Sites"] = structures
        return result

    def energy_filter(self, e_min, e_max, **kwargs):
        result = kwargs.get("Result", None)
        if result is None:
            result = self.get_data()
        result_filtered = {}
        energy_filtered = []
        cells_filtered = []
        sites_filtered = []
        formula_filtered = []
        for e_id in range(len(result["Energy"])):
            e_query = result["Energy"][e_id]
            if e_min is None and e_max is None:
                e_min = -math.inf
                e_max = math.inf
            elif e_min is None:
                e_min = e_max - 10
            elif e_max is None:
                e_max = e_min + 10
            if e_query > e_min and e_query < e_max:
                energy_filtered.append(result["Energy"][e_id])
                cells_filtered.append(result["Cells"][e_id])
                sites_filtered.append(result["Sites"][e_id])
                formula_filtered.append(result["Elements"][e_id])
        result_filtered["Formula"] = formula_filtered
        result_filtered["Energy"] = energy_filtered
        result_filtered["Cells"] = cells_filtered
        result_filtered["Sites"] = sites_filtered

    def element_filter(self, element, **kwargs):
        result = kwargs.get("Result", None)
        if result is None:
            result = self.get_data()
        result_filtered = {}
        energy_filtered = []
        cells_filtered = []
        sites_filtered = []
        formula_filtered = []
        elements = element.split("-")
        for e_id in range(len(result["Energy"])):
            system = []
            for i in result["Elements"][0]:
                system.append(i["symbols"][0])
            if set(elements).issubset(system):
                energy_filtered.append(result["Energy"][e_id])
                cells_filtered.append(result["Cells"][e_id])
                sites_filtered.append(result["Sites"][e_id])
                formula_filtered.append(result["Elements"][e_id])
        result_filtered["Formula"] = formula_filtered
        result_filtered["Energy"] = energy_filtered
        result_filtered["Cells"] = cells_filtered
        result_filtered["Sites"] = sites_filtered
        return result_filtered
