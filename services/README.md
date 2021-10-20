# Services
 
* If you plan to run each service separately, we recommend creating an [Anaconda](https://www.anaconda.com/products/individual) environment per service to manager its dependencies separately 
* Here we describe the implemented services 

## Summary

| Service Name  | localhost Port | Purpose  | Type | docker  | Status | 
| ------------- |:-------------:| -----:| -----:| -----:| -----:|
| Solver | 5000 | Core node solving semantic table annotation tasks  | Solver | Solver/5000 | |
| Autocorrect | 5005 | Fix typoes using different strategies that are enabled in config  | Util | Autocorrect/5000 |  | 
| Wikidata_Proxy | 5007 | encapsulates the lookup up and SPARQL query endpoint for Wikidata| Util | Wikidata_Endpoint_API/5000 | | 
| DBpedia_Proxy | 5003 | encapsulates the lookup up and SPARQL query endpoint for DBpedia | Util | Wikidata_Lookup_API/5000 | |
| Generic_Lookup | 5010 | Wikipedia_Lookup in the pre-computed lookup.db3 | Util | Generic_Lookup/5000 | |

* All services handles server errors (500), return it to Manager. Manager is a centeral point of errors 

## Service Types


### Util
* Stand-alone service with no dependencies on other services
* Reusable across Approaches 
* Examples:
    * Autocorrect
    * Wikidata_Proxy
    * DBpedia_Proxy

### Solver 
* Fat service
* Has **Solve** API, that recieved a table and solves it in terms of CEA, CTA and CPA
* **Solve** API is time scoped function using a configured SLA in seconds.
* Prepare a solution dictionary of the submission results, checkpoints and audit data (if any is enabled)
