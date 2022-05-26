# cazy-parser
*A way to extract specific information from the Carbohydrate-Active enZYmes.*

[![Downloads](https://pepy.tech/badge/cazy-parser)](https://pepy.tech/project/cazy-parser)
[![status](http://joss.theoj.org/papers/f709afe5d720fc6eee82fca277942a46/status.svg)](http://joss.theoj.org/papers/f709afe5d720fc6eee82fca277942a46)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/33f087332ec24da689268a13d2f4ca23)](https://www.codacy.com/gh/rvhonorato/cazy-parser/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rvhonorato/cazy-parser&amp;utm_campaign=Badge_Grade)
[![python lint](https://github.com/rvhonorato/cazy-parser/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/rvhonorato/cazy-parser/actions/workflows/lint.yml)
[![unittests](https://github.com/rvhonorato/cazy-parser/actions/workflows/unittests.yml/badge.svg?branch=main)](https://github.com/rvhonorato/cazy-parser/actions/workflows/unittests.yml)
[![codecov](https://codecov.io/gh/rvhonorato/cazy-parser/branch/master/graph/badge.svg?token=TO9EMMBIPL)](https://codecov.io/gh/rvhonorato/cazy-parser)

**Make sure to visit and cite the CAZy website**

* http://www.cazy.org/
* Lombard V, Golaconda Ramulu H, Drula E, Coutinho PM, Henrissat B (2014) The Carbohydrate-active enzymes database (CAZy) in 2013. **Nucleic Acids Res** 42:D490–D495. [PMID: [24270786](http://www.ncbi.nlm.nih.gov/sites/entrez?db=pubmed&cmd=search&term=24270786)].

License: [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

[RV Honorato. CAZy-parser a way to extract information from the Carbohydrate-Active enZYmes Database. *The Journal of Open Source Software*, 1(8), dec 2016.](https://github.com/openjournals/joss-papers/blob/master/joss.00053/10.21105.joss.00053.pdf)

doi: 10.21105/joss.00053


## Introduction
 *cazy-parser* is a tool that extract information from [CAZy](http://www.cazy.org/) in a more usable and readable format. Firstly, a script reads the HTML structure and creates a mirror of the database as a tab delimited file. Secondly, information is extracted from the database according to user inputted parameters and presented to the user as a set of accession codes.

## Install / Upgrade
```
$ pip install --upgrade cazy-parser
```


## Usage

*Internet connection required*


```
cazy-parser -h
usage: cazy-parser [-h] [-f FAMILY] [-s SUBFAMILY] [-c CHARACTERIZED] [-v] {GH,GT,PL,CA,AA}

positional arguments:
  {GH,GT,PL,CA,AA}

optional arguments:
  -h, --help            show this help message and exit
  -f FAMILY, --family FAMILY
  -s SUBFAMILY, --subfamily SUBFAMILY
  -c CHARACTERIZED, --characterized CHARACTERIZED
  -v, --version         show version
```

### Example

Extract all fasta sequences from family 43 of Glycoside Hydrolase subfamily 1

```
$ cazy-parser GH -f 43 -s 1
 [2022-05-26 16:39:21,511 91 INFO] ------------------------------------------
 [2022-05-26 16:39:21,511 92 INFO]
 [2022-05-26 16:39:21,511 93 INFO] ┌─┐┌─┐┌─┐┬ ┬   ┌─┐┌─┐┬─┐┌─┐┌─┐┬─┐
 [2022-05-26 16:39:21,511 94 INFO] │  ├─┤┌─┘└┬┘───├─┘├─┤├┬┘└─┐├┤ ├┬┘
 [2022-05-26 16:39:21,511 95 INFO] └─┘┴ ┴└─┘ ┴    ┴  ┴ ┴┴└─└─┘└─┘┴└─ v2.0.0
 [2022-05-26 16:39:21,511 96 INFO]
 [2022-05-26 16:39:21,511 97 INFO] ------------------------------------------
 [2022-05-26 16:39:21,511 183 INFO] Fetching links for Glycoside-Hydrolases, url: http://www.cazy.org/Glycoside-Hydrolases.html
 [2022-05-26 16:39:22,454 189 INFO] Only using links of family 43 subfamily 1
 [2022-05-26 16:39:23,029 26 INFO] Dowloading 1415 fasta sequences...
 [2022-05-26 16:40:32,187 51 INFO] Dumping fasta sequences to file GH43_1_26052022.fasta
```

This will generate the following file `GH43_1_DDMMYYY.fasta` containing the fasta sequences.

## To-do and how to contribute

Please refer to [CONTRIBUTING](CONTRIBUTING.md) (:
