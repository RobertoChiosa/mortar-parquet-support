# %%
from brickschema import Graph
import zipfile
from io import BytesIO
from urllib.request import urlopen 
import os
from string import Template

IMPORTS_URL = 'https://github.com/BrickSchema/Brick/releases/download/nightly/imports.zip'
USE_BRICK_NIGHTLY = True
BRICK_URL = "https://github.com/BrickSchema/Brick/releases/download/1.3.0/Brick.ttl"
PRINT_VALIDATION = False
DIR = os.path.dirname(os.path.realpath(__file__))

class UpdateInterface:

    def __init__(self, name: str, data_graph: Graph, ontology_graph: Graph):
        self.name = name

        self.data_graph = data_graph
        self.ontology_graph = ontology_graph

        self.full_graph = self.data_graph + self.ontology_graph
    
    def update_graph(self, query):
        self.full_graph.update(query)

    def validate(self):
        valid, report_graph, report = self.full_graph.validate()
        if PRINT_VALIDATION:
            print(f"Graph <{self.graph_path}> is valid? {valid}")
            if not valid:
                print("-" * 79)
                print(report)
                print("-" * 79)
        return valid, report_graph
    
    def save_clean_graph(self, filename):
        self.clean_graph = self.full_graph - self.ontology_graph
        self.fix_clean_namespaces()
        self.clean_graph.serialize(filename, format = 'ttl')

    def fix_clean_namespaces(self):
        self.clean_graph.bind(self.name, 'http://buildsys.org/ontologies/' + self.name + '#')
        #TODO: Fix when a '/' is in the point name (may be easier to just do this manually ...)

def get_ontology_graph():
    """
    returns skolemized graph with brick and imports
    """
    if USE_BRICK_NIGHTLY:
        g = Graph(load_brick_nightly=True)
    else:
        g = Graph(load_brick=BRICK_URL)
    response = urlopen(IMPORTS_URL)
    zip = zipfile.ZipFile(BytesIO(response.read()))

    for name in zip.namelist():
        g.parse(zip.read(name))
    
    return g.skolemize()

def format_area_query(report_graph):
    area_query_format = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
        PREFIX s223: <http://data.ashrae.org/standard223#>
        PREFIX unit: <http://qudt.org/vocab/unit/>
        PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
        PREFIX qudt: <http://qudt.org/schema/qudt/>
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

        DELETE {?this brick:value "$old" }
        INSERT {?this brick:value $new }
        WHERE {
        ?this brick:value "$old"
        }
        """
    res = report_graph.query(""" 
        select ?replace
        WHERE {
        ?s a sh:ValidationResult ;
            sh:value ?value .
        ?val brick:value ?replace .
        }
        """)
    
    if len(res) == 1:
        old = iter(res).__next__().get('replace')
        new = int(old.rsplit('^^')[0])
    else:
        raise ValueError('There is not 1 error that can be used to format area update')
    return Template(area_query_format).substitute(old=old, new=new)

def get_query_list():

    lev_p_sens_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Supply_Pressure_Sensor }
    INSERT {?this a brick:Pressure_Sensor ;
                brick:hasSubstance brick:Leaving_Chilled_Water }
    WHERE {
    ?this a brick:Supply_Pressure_Sensor   .
    }
    """

    ent_p_sens_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Return_Pressure_Sensor }
    INSERT {?this a brick:Pressure_Sensor ;
                brick:hasSubstance brick:Entering_Chilled_Water }
    WHERE {
    ?this a brick:Return_Pressure_Sensor   .
    }
    """


    # This may cause mistakes
    heating_demand_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Heating_Demand    }
    INSERT {?this a brick:Heating_Demand_Sensor }
    WHERE {
    ?this a brick:Heating_Demand   .
    }
    """


    # This may cause mistakes
    cooling_demand_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Cooling_Demand   }
    INSERT {?this a brick:Cooling_Demand_Sensor }
    WHERE {
    ?this a brick:Cooling_Demand   .
    }
    """


    # This may cause mistakes
    cooling_pct_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Cooling_Request_Percent_Setpoint  }
    INSERT {?this a brick:Leaving_Chilled_Water_Temperature_Setpoint }
    WHERE {
    ?this a brick:Cooling_Request_Percent_Setpoint  .
    }
    """


    # This may cause mistakes
    bldg26_pump_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Chilled_Water_Pump_VFD_Speed }
    INSERT {?this a brick:Motor_Speed_Sensor .}
    WHERE {
    ?this a brick:Chilled_Water_Pump_VFD_Speed .
    }
    """


    boiler_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Hot_Water_Supply_Flow_Sensor}
    INSERT {?this a brick:Hot_Water_Entering_Flow_Sensor ;
        a brick:Point . }
    WHERE {
    ?this a brick:Hot_Water_Supply_Flow_Sensor .
    }
    """


    r_coil_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE { ?this a brick:Reheat_Coil .
            ?vav brick:hasPart ?this .}
    INSERT { ?vav a brick:RVAV }
    WHERE {
        ?this a brick:Reheat_Coil .
        ?vav brick:hasPart ?this .
        }
    """

    #     Filter (?s = ?this) 
    #     BIND (?this as ?s)
    #     }
    # UNION
    #     {
    #     ?this a brick:Reheat_Coil .
    #     ?vav brick:hasPart ?this .
    #     Filter (?o = ?this) 
    #     BIND (?this as ?o)
    #     }
    # }
    # """


    chwr_ts_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Min_Chilled_Water_Supply_Temperature_Setpoint}
    INSERT {?this a brick:Min_Water_Temperature_Setpoint ; 
                brick:ofSubstance brick:Leaving_Chilled_Water }
    WHERE {
    ?this a brick:Min_Chilled_Water_Supply_Temperature_Setpoint
    }
    """

    chwsp_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Chilled_Water_Supply_Pressure}
    INSERT {?this a brick:Pressure_Sensor ;
                brick:hasSubstance brick:Leaving_Chilled_Water}
    WHERE {
        ?this a brick:Chilled_Water_Supply_Pressure
    }
    """
    chwrt_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Chilled_Water_Return_Pressure}
    INSERT {?this a brick:Pressure_Sensor ;
                brick:hasSubstance brick:Entering_Chilled_Water}
    WHERE {
        ?this a brick:Chilled_Water_Return_Pressure
    }
    """


    #bldg42: ASSUMING chilled water bypass valve refers to a bypass valve status
    #investigate this further
    bldg42_chwbp_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg42>

    DELETE {?this a brick:Chilled_Water_Bypass_Valve .
            ?chiller brick:hasPoint ?this .}
    INSERT {?this a brick:Bypass_Valve ;
                brick:hasSubstance brick:Chilled_Water;
                brick:hasPoint bldg:BypassValveStatus .
            bldg:BypassValveStatus a brick:Valve_Status .
            ?chiller brick:hasPart ?this .}
    WHERE {
        ?this a brick:Chilled_Water_Bypass_Valve.
        ?chiller brick:hasPoint ?this .
    }
    """


    oad_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Outside_Air_Damper_Command}
    INSERT {?this a brick:Damper_Command ;
                brick:hasSubstance brick:Outside_Air}
    WHERE {
        ?this a brick:Outside_Air_Damper_Command
    }
    """


    # ASSUMING MODE MEANS MODE STATUS
    mode_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Mode}
    INSERT {?this a brick:Mode_Status}
    WHERE {
        ?this a brick:Mode
    }
    """


    deprecation_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a ?class}
    INSERT {?this a ?newClass}
    WHERE {
    ?this a ?class .
    ?class owl:deprecated true .
    ?class brick:deprecatedInVersion ?depver .
    ?class brick:isReplacedBy ?newClass .
    }
    """


    #
    ft2_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this brick:hasUnits unit:FT_2}
    INSERT {?this brick:hasUnit unit:FT2}
    WHERE {
    ?this brick:hasUnits unit:FT_2
    }
    """


    chwv_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Chilled_Water_Valve_Command }
    INSERT {?this a brick:Valve_Command ;
                    brick:hasSubstance brick:Chilled_Water }
    WHERE {
    ?this a brick:Chilled_Water_Valve_Command
    }
    """


    hwv_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Hot_Water_Valve_Command }
    INSERT {?this a brick:Valve_Command ;
                    brick:hasSubstance brick:Hot_Water }
    WHERE {
    ?this a brick:Hot_Water_Valve_Command
    }
    """


    # ASSUMING that flow refers to a Sensor
    bldg4_supflow_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Supply_Air_flow }
    INSERT {?this a brick:Supply_Air_Flow_Sensor}
    WHERE {
    ?this a brick:Supply_Air_flow
    }
    """


    chws_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Chilled_Water_Supply_Temperature_Setpoint}
    INSERT {?this a brick:Supply_Chilled_Water_Temperature_Setpoint }
    WHERE {
    ?this a brick:Chilled_Water_Supply_Temperature_Setpoint
    }
    """


    chwr_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?this a brick:Chilled_Water_Return_Temperature_Setpoint}
    INSERT {?this a brick:Return_Chilled_Water_Temperature_Setpoint }
    WHERE {
    ?this a brick:Chilled_Water_Return_Temperature_Setpoint
    }
    """


    meters_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?meter brick:isPointOf ?this}
    INSERT {?meter brick:meters ?this }
    WHERE {
    ?meter a brick:Electrical_Meter ;
        brick:isPointOf ?this .
    }
    """


    electricalmeter_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {?meter a brick:Electric_Meter }
    INSERT {?meter a brick:Electrical_Meter  }
    WHERE {
    ?meter a brick:Electric_Meter 
    }
    """

    ordered_query_list = [heating_demand_fix, bldg42_chwbp_fix, ent_p_sens_fix, lev_p_sens_fix,
                    chwr_ts_fix, r_coil_fix, boiler_fix, bldg26_pump_fix, cooling_pct_fix, cooling_demand_fix,
                    chwsp_fix, chwrt_fix, oad_fix, mode_fix, chwv_fix, ft2_fix, bldg4_supflow_fix,
                    hwv_fix, chws_fix, chwr_fix, meters_fix, electricalmeter_fix, meters_fix, deprecation_fix]
    
    return ordered_query_list

def get_building_specific_query_dict():
    queries = {}

    # ASSUMING EVERYTHING WITH RM, WITH NO DECLARED TYPE, IS A ZONE
    # FOR BLDG6 SPECIFICALLY
    bldg6_rm_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg1>

    DELETE {}
    INSERT {?this a brick:HVAC_Zone }
    WHERE {
        ?this brick:hasPoint ?that .
        FILTER REGEX (str(?this), "VAVRM") .
        FILTER NOT EXISTS {
            ?this a ?y .
    }
    }
    """

    bldg43_add_chiller_fix = """
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX g36: <http://data.ashrae.org/standard223/1.0/extension/g36#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bldg: <http://buildsys.org/ontologies/bldg43>

    INSERT DATA {<http://buildsys.org/ontologies/bldg43#chiller> a brick:Chiller }
    """

    queries['bldg43'] = [bldg43_add_chiller_fix]
    queries['bldg6'] = [bldg6_rm_fix]
    return queries

def run_updates():
    """
    uses ordered query list to update all graphs. Some updates apply only to specific files
    """

    ontology_graph = get_ontology_graph()
    query_list = get_query_list()
    building_specific_query_dict = get_building_specific_query_dict()

    for file in os.listdir('graphs'):
        try:
            path = os.path.join(DIR, 'graphs', file)
            name = file.split('.')[0]
            print(name)
            data_graph = Graph().parse(path)
            bv = UpdateInterface(ontology_graph=ontology_graph, data_graph=data_graph, name = name)

            for q in query_list:
                bv.update_graph(q)
            
            specific_query_list = building_specific_query_dict.get(name)
            
            if specific_query_list:
                for q in specific_query_list:
                    bv.update_graph(q)

            valid, report_graph = bv.validate()
            
            if valid:
                bv.save_clean_graph(os.path.join(DIR, 'graphs_updated', file))
                continue

            area_query = format_area_query(report_graph)
            bv.update_graph(area_query)
            valid, final_report = bv.validate()

            if not valid:
                raise ValueError('Not Validated')
            
            bv.save_clean_graph(os.path.join(DIR, 'graphs_updated', file))
            
        except ValueError:
            print(f'{path} not a valid graph')

if __name__ == "__main__":
    run_updates()