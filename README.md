# cazy-parser
*A way to extract specific information from the Carbohydrate-Active enZYmes.*

If you are using this tool, **make sure to cite and visit CAZy website**

* http://www.cazy.org/
* Lombard V, Golaconda Ramulu H, Drula E, Coutinho PM, Henrissat B (2014) The Carbohydrate-active enzymes database (CAZy) in 2013. **Nucleic Acids Res** 42:D490–D495. [PMID: [24270786](http://www.ncbi.nlm.nih.gov/sites/entrez?db=pubmed&cmd=search&term=24270786)].

### Introduction
 *cazy-parser* is a tool that extract information from CAZy in a more usable and readable format. Firstly, a script reads the HTML structure and creates a mirror of the database as a tab delimited file. Secondly, information is extracted from the database according to user inputted parameters and presented to the user as a multifasta.

### Dependencies

* Python 2.x
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) module

### Usage

*Both steps require an internet conection*

1) Database creation

`$ python create-cazy-db.py`

2) Extract sequences

`$ python select-cazy-sequences --db <database>`
* Options:

`--family` Family to be searched, case sensitive

`--subfamilies` Create a multifasta for each subfamily

`--characterized` Create a multifasta containing only characterized enzymes

### Examples

1) Extract all sequences from family 9 of Glycosyl Transferases.

`$ python select-cazy-sequences --db CAZy_DB_xx-xx-xxxx.csv --family GT9`

This will generate the following files:
```
GT9.fasta
```

2) Extract all sequences from family 43 of Glycoside Hydrolase, including subfamilies

`$ python select-cazy-sequences --db CAZy_DB_xx-xx-xxxx.csv --family GH43 --subfamilies`

This will generate the following files:

```
GH43.fasta
GH43_sub1.fasta
(...)
GH43_sub37.fasta
```

3) Extract all sequences from family 42 of Polysaccharide Lyases including characterized entries

`$ python select-cazy-sequences --db CAZy_DB_xx-xx-xxxx.csv --family PL42 --characterized`

This will generate the following files:

```
PL42.fasta
PL42_characterized.fasta
```

### To-do

1. Extract sequences based on organism/domain
2. Select structural data

### Known bugs

None (yet).

#### Contact info

If there are any inquires please contact me on *rvhonorato at gmail.com*
