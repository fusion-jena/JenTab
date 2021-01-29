# Baseline Approach
This service provides an iteratrive lookup-based as a baseline approach. It solves the tabluar data to knowledge graph matching in 3 tasks: 
* Cell Entity Assignment (CEA)
* Column Type Assignment (CTA)
* Column Property Assignment (CPA)

## Supported Knowledge Graphs:
* Wikidata
* DBpedia


## Endpoints Explained 
* Supports one core endpoint named: **solve**
* A processed version of a CSV file, refered as table, is a common type for the 3 endpoints. An explained example is like the following:
    * table (json):   
        * ```json
          {"orientation": "Horizontal", "header": ["col0", "col1", "col2", "col3"], 
          "name": "0007GMF5", 
          "data": 
          {"col0": {
              "original_cell_vals": ["col0", "Rhein-Berg District", "Rhein-Kreis Neuss", ...], 
              "lang": "de", 
              "type": "OBJECT", 
              "clean_cell_vals": ["col0", "Rhein_Berg_District", "Rhein_Kreis_Neuss", ...], 
              "autocorrect_cell_vals": ["cold", "", "", "annexe_Ruhr_Kreis", "", ...]}, 
          "col1": {
            "original_cell_vals": ["col1", "Bergisch Gladbach", "Neuss", ...],   
            "lang": "en", 
            "type": "OBJECT", 
            "clean_cell_vals": ["col1", "Bergisch_Gladbach", "Neuss", ...], 
            "autocorrect_cell_vals": ["cold", "Begich_Gladbach", ... ]},  
           ...
          }}
          ```
        * cea_t_cols (list of int/str(int)):
            * target columns 
            * ```json
              ["0", "1", "2", "3", "0", "1", "2", "3", "0", "1", "2", "3", "0", "1", "2", "3"]
              ```
        * cea_t_rows (list of int/str(int)):
            * target rows        
            * ```json
              ["1", "1", "1", "1", "2", "2", "2", "2", "3", "3", "3", "3", "4", "4", "4", "4"]
              ```
        * cta_t_cols (list of int/str(int)):
            * target columns 
            * ```json
                ["0"]
              ```
        * cpa_t_subjs (list of int/str(int)):
            * target **subject** columns 
            * ```json
                ["0", "0", "0"]
              ```
        * cpa_t_objs (list of int/str(int)):
            * target **object** columns 
            * ```json
                ["1", "2", "3"]
              ```
* **Output**:
    * Tasks mappings dict (json)
    * One entity mention (URI) per cell (col/row)
    * One column type per col
    * One property per sub/obj 
    * Format:
        * ```json
          {"cea": [{"col_id":..., "row_id":..., "mapped":...}] ,
           "cta": [{"col_id": .., "mapped": ...}],
           "cpa": [{"subj_id": ..., "obj_id": ..., "mapped": ...}, ...]
          } 
        ```
## Internal Storage (Deprecated)
* All retrieved mappings for the three tasks are stored on disk `internal_storage`.
* If a table has a stored mappings in the `internal_storage` , then retrieve it directly. Otherwise, a Lookup service will be fired.
* Supports a Table-level caching.
* Intermediate results are also saved, if we need to change the top level implementation, i.e., majority voting in CTA to something else, it should be quicker due to re-hitting the lookup service.
* Internal_storage is supported for each knowledge graph (Wikidata & DBpedia). A table can have mappings from both KG.
* Structure:   
```bash
Wikidata_Lookup
└───internal_storage
    ├───CEA
    │   ├───plain
    │   │   ├───all_token_cell_lookup
    │   │   ├───autocorrect_lookup
    │   │   ├───full_cell_lookup
    │   │   ├───selective_lookup
    │   │   └───token_cell_lookup
    │   └───revisit
    │       ├───all_token_cell_lookup
    │       ├───autocorrect_lookup
    │       ├───full_cell_lookup
    │       ├───selective_lookup
    │       └───token_cell_lookup
    ├───CPA
    │   ├───cell_props
    │   └───col_props
    └───CTA
        ├───cell_types
        └───col_types
```
## Configurations
* **assets**
    * download the NLTK [stopwords](https://gist.github.com/sebleier/554280) and add it under `assets` folder
* **config.py** 
 
| Name                  | Default | Description                                                                |
|-----------------------|---------|----------------------------------------------------------------------------|
| run_mode | 1       | 1 for local host and 0 for Docker |
| *_PATH (Deprecated)    | *      | Defines the default paths of the internal_storage, for saving intermediate results                                |
| OBJ_COL           | "OBJECT"      | The name of the column type, core columns, if no targets (cols/rows) are specific, we rely on this column type to generate mappings |
| MAX_TOKENS           | 5      | One strategy which tries to get cells URIs tokenizes the the cell values and compute all different combinations in an accumaltive order |
| TARGET_KG           | WIKIDATA       | Specifies which KG we ask for mappings. Options DBPEDIA = 1 & WIKIDATA = 2 |

## External Service
* Baseline Approach depends on 4 services (lookups and endpoints) of the target knowledge graph.
* see [\external_services](external_services) default configurations
 
| KG                  | Service | Description                   | APIs | 
|-----------------------|---------|----------------------------------------------------------------------------|----- |
| DBpedia   | DBpedia_Endpoint_Service | proxy for the DBpedia SPARQL endpoint |get_type_for, get_type_for_lst, get_subclasses_for, get_parents_for |
| DBpedia | DBpedia_Lookup_Service | proxy for the DBpedia lookup    |  look_for, look_for_lst |
| Wikidata | Wikidata_Lookup_Service | proxy for the Wikidata lookup endpoint |   look_for, look_for_lst |
| Wikidata | Wikidata_Endpoint_Service | proxy for the endpoint |   get_type_for, get_type_for_lst, get_subclasses_for, get_parents_for, get_connection_for_lst |


