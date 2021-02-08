# Baseline Approach
This service provides an iteratrive lookup-based as a baseline approach. It solves the tabluar data to knowledge graph matching in 3 tasks: 
* Cell Entity Assignment (CEA)
* Column Type Assignment (CTA)
* Column Property Assignment (CPA)

## Supported Knowledge Graphs:
* Wikidata


## Endpoints Explained 
### `POST /solve`
* A processed version of a CSV file, refered as table. An explained example is like the following:
    * table (json):   
        * ```json
          {"orientation": "Horizontal", "header": ["col0", "col1", "col2", "col3"], 
          "name": "0007GMF5", 
          "data": 
          {"col0": {
              "original_cell_vals": ["col0", "Rhein-Berg District", "Rhein-Kreis Neuss", ...], 
              "lang": "de", 
              "type": "OBJECT", 
              "clean_cell_vals": ["col0", "Rhein_Berg_District", "Rhein_Kreis_Neuss", ...]}, 
          "col1": {
            "original_cell_vals": ["col1", "Bergisch Gladbach", "Neuss", ...],   
            "lang": "en", 
            "type": "OBJECT", 
            "clean_cell_vals": ["col1", "Bergisch_Gladbach", "Neuss", ...]},  
           ...
          }}
          ```
        * cea_t_cols (list of int/str(int)):
            * target columns of CEA task
            * ```json
              ["0", "1", "2", "3", "0", "1", "2", "3", "0", "1", "2", "3", "0", "1", "2", "3"]
              ```
        * cea_t_rows (list of int/str(int)):
            * target rows of CEA task      
            * ```json
              ["1", "1", "1", "1", "2", "2", "2", "2", "3", "3", "3", "3", "4", "4", "4", "4"]
              ```
        * cta_t_cols (list of int/str(int)):
            * target columns of CTA task
            * ```json
                ["0"]
              ```
        * cpa_t_subjs (list of int/str(int)):
            * target **subject** columns of CPA task
            * ```json
                ["0", "0", "0"]
              ```
        * cpa_t_objs (list of int/str(int)):
            * target **object** columns of CPA task
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
      
## Configurations
* **assets**
    * stopwords, check [assets](/assets)
* **config.py** 
 
| Name                  | Default | Description                                                                |
|-----------------------|---------|----------------------------------------------------------------------------|
| run_mode | 1       | 1 for local host and 0 for Docker |
| OBJ_COL           | "OBJECT"      | The name of the column type, core columns, if no targets (cols/rows) are specific, we rely on this column type to generate mappings |
| MAX_TOKENS           | 5      | One strategy which tries to get cells URIs tokenizes the the cell values and compute all different combinations in an accumaltive order |
| TARGET_KG           | WIKIDATA       | Specifies which KG we ask for mappings. Options DBPEDIA = 1 & WIKIDATA = 2 |
| DEDUCE_FROM_TARGETS           | True       | Force solving for the given targets of each task and don't rely on the predicted OBJECT column as the subject column|
| LABELS_FOR_BATCH_SIZE           | 100,000       | Maximum (batch_size) instances we retrieve labels for, prevents timeout and blocking IPs by public service.|
| PIPELINE_SLA_SEC           | 60 * 60 (1 Hour)       | Time in (mins) pipeline should take to finish one table, if exceeded, Timeout exception will be raised. Prevents execution to infinity. Pipeline saves it's progress in intermediate steps.|
| ENABLE_PARTIAL_RES_SUBMISSION           | True       | If the pipeline failed to solve a given table for the given SLA, 1 hour, it will submit the intermediate and incomplete results to Manager.|
| LCS_SELECT_CTA           | True       | This boolean decides which method is used to select CTA. **True** will activate **LCS** method. **False** will activate **majority vote** method |  

* In addition to the configuration table above, we also support a configuration for our supported strategies which obtain queries from a given cell
    * for more details about how these strategies are used, kindly refer to our [paper](https://github.com/fusion-jena/JenTab#materials).  

## External Services
* Baseline Approach depends on 4 services including data sources of the target knowledge graph.
* see [\external_services](external_services) default configurations
 
| KG                  | Service | Description                   | APIs | 
|-----------------------|---------|----------------------------------------------------------------------------|----- |
| Wikidata_Lookup_Service | (data source) proxy for the Wikidata lookup endpoint |   look_for, look_for_lst |
| Wikidata_Endpoint_Service | (data source) proxy for the endpoint |   get_type_for, get_type_for_lst, get_subclasses_for, get_parents_for, get_connection_for_lst |
| Generic_Lookup | proxy for our precomputed lookup. Our primary method solving typoes.    |  look_for, look_for_lst |
| Autocorrect | In case of Generic_Lookup failure, this is our secondary and on demand service fixing typoes |get_type_for, get_type_for_lst, get_subclasses_for, get_parents_for |

