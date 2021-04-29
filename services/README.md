# Services
 
* If you plan to run each service separately, we recommend creating an [Anaconda](https://www.anaconda.com/products/individual) environment per service to manager its dependencies separately 
* Here we describe the implemented services 

## Summary

| Service Name  | localhost Port | Purpose  | Type | docker  | Status | 
| ------------- |:-------------:| -----:| -----:| -----:| -----:|
| Baseline_Approach | 5000 | Lookup based approach with majority voting  | Approach | Baseline_Approach/5000 | |
| CleanCells | 5001 | clean cell values and fix encoding issues  | Preprocessing | CleanCells/5000 | |
| LanguagePrediction | 5004 | Predits languge of texts  | Preprocessing | LanguagePrediction/5000 | |
| TypePrediction | 5006 | Simple NER system, classifies col types | Preprocessing | TypePrediction/5000 | |
| Autocorrect | 5005 | Fix typoes using different strategies that are enabled in config  | Util | Autocorrect/5000 |  | 
| Wikidata_Endpoint_API | 5007 | Wikidata SPARQL query endpoint | Util | Wikidata_Endpoint_API/5000 | | 
| Wikidata_Lookup_API | 5008 | Wikidata lookup, fuzzy search | Util | Wikidata_Lookup_API/5000 | |
| Generic_Lookup | 5010 | Wikipedia_Lookup in the pre-computed lookup.db3 | Util | Generic_Lookup/5000 | |

* All services handles server errors (500), return it to Manager. Manager is a centeral point of errors 

## Service Types


### Util
* Stand-alone service with no depedencies on other services
* Reusable across Approaches 
* Examples:
    * Autocorrect
    * Wikidata_Endpoint_API
    * Wikidata_Lookup_API

### Preprocessing
* Naive services used in preprocessing phase 
* If preprocessing take place in offline mode, then, these services are not required for the App
* Our preprocessing pipeline consists of 4 services
* Examples:
    * TypePrediction
    * LanguagePrediction
    * CleanCells

### Approach 
* Fat service
* Has **Solve** API, that recieved a table and solves it in terms of CEA, CTA and CPA
* **Solve** API is time scoped function using a configured SLA in seconds.
* Prepare a solution dictionary of the submission results, checkpoints and audit data (if any is enabled)
