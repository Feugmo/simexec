import json
import math
from weakref import KeyedRef

from aiida import load_profile
from aiida.orm import CalcJobNode, Dict, QueryBuilder, StructureData, load_node
from aiida.tools.visualization.graph import Graph


class db_query:
    def get_all_data(self):
        """
        function don't have input, the output of the function is a list of list
        list 1: list of Structure data node (AIIDA type, you can find all properties to each strcutre checking those properties by using dir)
        list 2: list of result data node (AIIDA Type) where the calculation result such as energy is stored
        list 3: list of calculation node stored (AIIDA type) where you can find the type of the calculation such as Optmiziation...

        All the result is filtered based on the "result" list 3. Due to structure data can include one created and created but not used, calculation node can
        also contain one that is Killed or created (which make the result the limiting num (the smallest among three))

        The relationship data are collected using "Advance quer" in query builder
        """
        load_profile()
        res = QueryBuilder()
        res.append(Dict, tag="dict")
        res.append(StructureData, with_descendants="dict")
        # Could use some optimization
        cal = QueryBuilder()
        cal.append(Dict, tag="res")
        cal.append(CalcJobNode, with_descendants="res")
        qb = QueryBuilder()
        qb.append(CalcJobNode, tag="calcjob")
        qb.append(Dict, with_incoming="calcjob")
        return [res.all(), qb.all(), cal.all()]

    def element_filter(self, element):
        whole_data = self.get_all_data()
        items = []
        energys = []
        ele_num = {}
        elements = element.split("-")
        for ele in elements:
            ele_num[ele] = []
        for structure, energy, calcu in zip(whole_data[0], whole_data[1], whole_data[2]):

            if element == "All":
                structure = structure[0].get_pymatgen()
                item = {}
                item["Space_G"] = str(structure.get_space_group_info())
                item["Formula"] = structure.formula
                item["Cal_Type"] = str(calcu[0].process_type.split(":")[1])
                item["UUID"] = str(calcu[0].uuid)
                try:
                    e_query = round(energy[0].attributes["energy"], 3)
                except KeyError:
                    e_query = round(energy[0].get_dict()["total_energies"]["energy_extrapolated"], 3)
                item["Energy"] = e_query
                items.append(item)
            else:
                if set(elements).issubset(set(structure[0].get_kind_names())):

                    y = structure[0].get_composition()
                    structure = structure[0].get_pymatgen()
                    for i in y:
                        try:
                            ele_num[i].append(y[i])
                        except KeyError:
                            ele_num[i] = [y[i]]
                    item = {}
                    item["Space_G"] = str(structure.get_space_group_info())
                    item["Formula"] = structure.formula
                    item["Cal_Type"] = str(calcu[0].process_type.split(":")[1])
                    item["UUID"] = str(calcu[0].uuid)
                    try:
                        e_query = round(energy[0].attributes["energy"], 3)
                    except KeyError:
                        e_query = round(energy[0].get_dict()["total_energies"]["energy_extrapolated"], 3)
                    item["Energy"] = e_query
                    items.append(item)
                    try:
                        energys.append(round(energy[0].attributes["energy"], 3))
                    except KeyError:
                        energys.append(round(energy[0].get_dict()["total_energies"]["energy_extrapolated"], 3))
            ratios = {"ratio": []}
            # Try to solve the problem regarding if compounment only has one kind of element, the following will not be compatible with compound over
            for r in range(len(ele_num[elements[0]])):
                """type: is the molecule count for each element, the reason for doing this is to avoid confusion on element order e.g,
                first calculated may be Mg but on the list it may be "Al" considering a method to remove that constraint"""
                try:
                    E_ratio = ele_num[list(ele_num.keys())[0]][r] / (
                        ele_num[list(ele_num.keys())[1]][r] + ele_num[list(ele_num.keys())[0]][r]
                    )
                    ratios["ratio"].append(
                        [
                            E_ratio,
                            energys[r],
                        ]
                    )
                    ratios["type"] = [ele_num[list(ele_num.keys())[0]], ele_num[list(ele_num.keys())[1]]]
                except IndexError:
                    E_ratio = 1
                    ratios["ratio"].append(
                        [
                            E_ratio,
                            energys[r],
                        ]
                    )
                ratios["type"] = [ele_num[list(ele_num.keys())[0]]]

        return [json.dumps(items), json.dumps(ratios), json.dumps(ele_num)]

    def energy_filter(self, **kwargs):
        # if error happen to Cal_type remove the .split(":")[1], which is used to extract type and shorten the output
        """
        This function has no required input,
        Optional input including e_min and e_max, which represent the minimum and maximum energy you want to query on respectively

        the output is a json type
        Key word contains: Cell, Formula, Calculation Type (Cal_type), UUID, Energy

        """
        e_min = kwargs.get("energy_min", None)
        e_max = kwargs.get("energy_max", None)
        whole_data = self.get_all_data()
        items = []
        for structure, energy, calcu in zip(whole_data[0], whole_data[1], whole_data[2]):
            if e_min is None and e_max is None:
                e_min = -math.inf
                e_max = math.inf
            elif e_min is None:
                e_min = e_max - 10
            elif e_max is None:
                e_max = e_min + 10
            try:
                e_query = round(energy[0].attributes["energy"], 3)
            except KeyError:
                e_query = round(energy[0].get_dict()["total_energies"]["energy_extrapolated"], 3)
            if e_query > e_min and e_query < e_max:
                item = {}
                item["Space_G"] = str(structure[0].get_pymatgen().get_space_group_info())
                item["Formula"] = structure[0].get_formula()
                item["Cal_Type"] = str(calcu[0].process_type.split(":")[1])
                item["UUID"] = str(calcu[0].uuid)
                item["Energy"] = e_query
                items.append(item)
        return json.dumps(items)

    def fetch_process(self):
        """
        This function has no input,
        the output of the function is a list contains 2 json type,
        the first is the Json contains the information of the calculation node
        key contains: Cal_type, Status, and Time
        the second is the Json contains the count of each type of calculation
        """
        load_profile()
        qb = QueryBuilder()  # Instantiating instance
        qb.append(CalcJobNode)
        qb.order_by({CalcJobNode: {"ctime": "desc"}})
        cal_nodes = qb.all()
        items = []
        # 3 Process Types
        status = {}
        cal_type_list = []
        users = []
        for calcu in cal_nodes:
            item = {}
            calculation_type = str(calcu[0].process_type.split(":")[1])
            process_type = str(calcu[0].process_state).split(".")[1]
            user = str(calcu[0].computer).split(",")[0]
            item["Cal_Type"] = calculation_type
            item["Time"] = str(calcu[0].ctime.strftime("%m/%d/%y %H:%M"))
            item["Status"] = process_type
            item["Computer"] = user
            if calculation_type not in cal_type_list:
                cal_type_list.append(calculation_type)
            if user not in users:
                users.append(user)
            try:
                status[process_type] += 1
            except KeyError:
                status[process_type] = 1
            item["UUID"] = str(calcu[0].uuid)
            items.append(item)
        return [
            json.dumps(items),
            json.dumps(
                {"Status": list(status), "Status_num": list(status.values()), "Types": cal_type_list, "User": users}
            ),
        ]

    def UUID_Detailed_Info(self, calc_nodes):
        load_profile()
        calc_node = load_node(calc_nodes)
        structure_node = load_node(calc_node.inputs.structure.uuid).get_pymatgen_structure()
        try:
            result_node = load_node(calc_node.outputs.results.uuid)
        except AttributeError:
            result_node = calc_node.outputs.misc
        item = {}
        item_gen = {}
        item_str = {}
        # item['Cell']=str(structure_node.cell)
        item_str["space_group"] = str(structure_node.get_space_group_info())
        item["Formula"] = str(structure_node.formula)
        item_gen["Cal_Type"] = str(calc_node.process_type.split(":")[1])
        item_str["Molecules"] = str(structure_node.num_sites)
        item_str["Chem_System"] = str(structure_node.composition.chemical_system)
        # item['Energy']=round(result_node.attributes['energy'],3)
        item_gen["Computer"] = str(calc_node.computer).split(",")[0]
        item_gen["Time"] = str(calc_node.ctime.strftime("%m/%d/%y %H:%M"))  # Start Time
        item_gen["WorkDir"] = str(calc_node.get_remote_workdir())
        item_gen["Ftime"] = str(calc_node.mtime.strftime("%m/%d/%y %H:%M"))
        item_str["Density"] = str(round(structure_node.density, 1))
        item_str["Volume"] = str(round(structure_node.volume, 1))
        final_value = []
        final_key = []
        try:
            result_det = result_node.attributes

        except KeyError:
            result_det = list(result_node.get_dict())

        for det in result_det:
            if type(result_det[det]) == dict:
                final_key += list(result_det[det])
                final_value += [str(i) for i in result_det[det].values()]
            else:
                final_key.append(det)
                final_value.append(str(result_det[det]))

        item["Result_key"] = final_key
        item["Result_value"] = final_value
        item["StructureInfo"] = item_str
        item["GeneralInfo"] = item_gen
        item["Retrived_list"] = calc_node.outputs.retrieved.base.repository.list_object_names()

        return json.dumps(item)

    def process_plot_gen(self, uuid):
        g = Graph(node_id_type="uuid")
        g.recurse_descendants(
            uuid,
        )
        g.recurse_ancestors(uuid)
        g.graphviz.render(format="png", directory="graph", filename=uuid).replace("\\", "/")
        print("Graph Generated")
