# cazy-parser
*A way to extract specific information from the Carbohydrate-Active enZYmes.*

[![Downloads](https://pepy.tech/badge/cazy-parser)](https://pepy.tech/project/cazy-parser)  [![status](http://joss.theoj.org/papers/f709afe5d720fc6eee82fca277942a46/status.svg)](http://joss.theoj.org/papers/f709afe5d720fc6eee82fca277942a46) [![DOI](https://zenodo.org/badge/65995178.svg)](https://zenodo.org/badge/latestdoi/65995178)

License: [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

**If you are using this tool please read and cite the paper!**

[RV Honorato. CAZy-parser a way to extract information from the Carbohydrate-Active enZYmes Database. *The Journal of Open Source Software*, 1(8), dec 2016.](https://github.com/openjournals/joss-papers/blob/master/joss.00053/10.21105.joss.00053.pdf)

doi: 10.21105/joss.00053

**Also make sure to visit and cite the CAZy website**

* http://www.cazy.org/
* Lombard V, Golaconda Ramulu H, Drula E, Coutinho PM, Henrissat B (2014) The Carbohydrate-active enzymes database (CAZy) in 2013. **Nucleic Acids Res** 42:D490–D495. [PMID: [24270786](http://www.ncbi.nlm.nih.gov/sites/entrez?db=pubmed&cmd=search&term=24270786)].

_____

## Changelog
v1.3 - Oct 7, 2018 - Added progress bars since creating the database takes a long time and might look stuck

v1.2 - Aug 18, 2017 - Fixed (yet) another bug when parsing page indexes

v1.1 - May 24, 2017 - Fixed bug when identifying page indexes

v1.0 - Oct 21, 2016 - First release

## Introduction
 *cazy-parser* is a tool that extract information from [CAZy](http://www.cazy.org/) in a more usable and readable format. Firstly, a script reads the HTML structure and creates a mirror of the database as a tab delimited file. Secondly, information is extracted from the database according to user inputted parameters and presented to the user as a set of accession codes.

## Installation
`$ pip install cazy-parser`

or

Download latest source from [this link](https://pypi.python.org/pypi/cazy-parser)

```
$ tar -zxvf cazy-parser-x.x.x.tar.gz
$ cd cazy-parser-x.x.x
$ python setup.py install
```
## Usage

*Please note that both steps require an internet conection*

1) Database creation

`$ create_cazy_db`

(-h for help)
* This script will parse the [CAZy](http://www.cazy.org/) database website and create a comma separated table containing the following information:
    * domain
    * protein_name
    * family
    * tag *(characterized status)*
    * organism_code
    * [EC](http://www.enzyme-database.org/) number (ec stands for enzyme comission number)
    * [GENBANK](https://www.ncbi.nlm.nih.gov/genbank/) id
    * [UNIPROT](uniprot.org) code
    * subfamily
    * organism
    * [PDB](http://www.rcsb.org/) code

2) Extract sequences

* Based on the previously generated csv table, extract accession codes for a given protein family.

`$ extract_cazy_ids --db <database> --family <family code>`

(-h for help)
* Optional:

`--subfamilies` Create a file for each subfamily, default = False

`--characterized` Create a file containing only characterized enzymes, default = False

## Usage examples

1) Extract all accession codes from family 9 of Glycosyl Transferases.

`$ extract_cazy_ids --db CAZy_DB_xx-xx-xxxx.csv --family GT9`

This will generate the following files:
```
GT9.csv
```

2) Extract all accession codes from family 43 of Glycoside Hydrolase, including subfamilies

`$ extract_cazy_ids --db CAZy_DB_xx-xx-xxxx.csv --family GH43 --subfamilies`

This will generate the following files:

```
GH43.csv
GH43_sub1.csv
GH43_sub2.csv
GH43_sub3.csv
(...)
GH43_sub37.csv
```

3) Extract all accession codes from family 42 of Polysaccharide Lyases including characterized entries

`$ extract_cazy_ids --db CAZy_DB_xx-xx-xxxx.csv --family PL42 --characterized`

This will generate the following files:

```
PL42.fasta
PL42_characterized.fasta
```

## To-do and how to contribute

Please refer to CONTRIBUTE.md


### Known bugs

None, yet.

#### Contact info

If there are any inquires please contact me on *rvhonorato at gmail.com*
