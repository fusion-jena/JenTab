# Assets

* Assets folder holds your input data for rounds and any external static dependencies for the other services.
* For the input configuration please refer to the [dataset](https://zenodo.org/record/4282879#.YIrI57UzZZg) provided by the challenge.
* **Directory Structure** below explains the assets structure either the input files for each round or for the other services.
* **Dependencies** lists the external dependencies to download. 

## Directory Structure
	'''
	+---Autocorrect
	|       GoogleNews-vectors-negative300.bin
	|       
	+---Baseline_Approach
	|       stopwords.txt
	|       
	+---data
	|   +---cache
	|   |   \---Generic_Lookup
	|   |           lookup.db3
	|   |           
	|   \---input
	|       \---2020
	|           +---Round 1
	|           |   +---tables
	|           |   \---targets
	|           +---Round 2
	|           |   +---tables
	|           |   \---targets
	|           +---Round 3
	|           |   +---tables
	|           |   \---targets
	|           \---Round 4
	|               +---tables
	|               \---targets
	\---Wikidata_Endpoint
			excluded_classes.csv
			excluded_colheaders.csv

	'''
	
## Dependencies
* [GoogleNews-vectors-negative300.bin](https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz)
* [stopwords.txt](https://gist.github.com/sebleier/554280)
* [2020 Dataset per Round](https://www.cs.ox.ac.uk/isg/challenges/sem-tab/2020/index.html)
* [Generic_Lookup per Round](https://github.com/fusion-jena/JenTab_precomputed_lookup) "lookup.db3" in the Directory Structure
* Wikidata_Endpoint
	* [excluded_classes.csv](https://github.com/fusion-jena/JenTab/blob/main/assets/Wikidata_Endpoint/excluded_classes.csv)
	* [excluded_colheaders.csv](https://github.com/fusion-jena/JenTab/blob/main/assets/Wikidata_Endpoint/excluded_colheaders.csv)


