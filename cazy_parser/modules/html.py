import itertools
import logging
import os
import re
import string
import sys
import urllib

import requests
from bs4 import BeautifulSoup

from cazy_parser.utils import init_bar

log = logging.getLogger("cazylog")


def fetch_data(link_list):
    """
    Parse list of links and extract information.

    Parameters
    ----------
    link_list : list
        List of links to parse


    Returns
    -------
    data : list
        List of dictionaries containing information about each entry.

    """

    data = []
    for _, link in enumerate(link_list):
        if ".txt" in link:
            link_data = get_data_from_txt(link)
        else:
            link_data = get_data_from_html(link)

        data.append(link_data)

    return list(itertools.chain(*data))


def parse_td(td_list):
    """
    Parse a table from the HTML page.

    Parameters
    ----------
    td_list : list
        List of table elements.

    Returns
    -------
    data_dict : dic
        Dictionary of data.

    """
    data_dict = {}
    if len(td_list) <= 1 or td_list[0].text == "Protein Name":
        # this is likely the header
        return data_dict

    protein_name = td_list[0].text
    ec = td_list[1].text
    # referece = td_list[2].text
    organism = td_list[3].text
    try:
        genbank = td_list[4].find("a").text
    except AttributeError:
        genbank = "unavailable"

    uniprot = td_list[5].text
    pdb = td_list[6].text

    data_dict["protein_name"] = protein_name
    data_dict["ec"] = ec
    data_dict["organism"] = organism
    data_dict["genbank"] = genbank
    data_dict["uniprot"] = uniprot
    data_dict["pdb"] = pdb

    return data_dict


def parse_table(table):
    """
    Parse a beautiful soup table and retrieve information.

    Parameters
    ----------
    table : bs4.element.Tag
        Beautiful soup table.

    Returns
    -------
    table_data : list
        List of dictionaries containing information from the table.

    """
    table_data = []
    for tr in table.findAll("tr"):
        tds = tr.findAll("td")
        td_dic = parse_td(tds)
        table_data.append(td_dic)
    return table_data


def get_data_from_html(link):
    """
    Retrieve information from the HTML page.

    Parameters
    ----------
    link : str
        Link to the page.

    """
    soup = BeautifulSoup(urllib.request.urlopen(link), features="html.parser")
    table = soup.find("table", attrs={"class": "listing"})
    domain = ""
    family = link.split(".org/")[-1].split("_")[0]
    data_list = parse_table(table)

    tag = "characterized" if "characterized" in link else ""
    # add more information to the data
    for data in data_list:
        data["tag"] = tag
        data["family"] = family
        data["domain"] = domain

    return data_list


def get_data_from_txt(link):
    """
    Retrieve information from the TXT file.

    Parameters
    ----------
    link : str
        Link to the page.

    Returns
    -------
    data_list : list
        List of dictionaries containing information from the TXT file.

    """
    data_list = []
    response = requests.get(link)
    tag = "characterized" if "characterized" in link else ""
    for line in response.text.split(os.linesep):
        data_dict = {}
        data = line.split("\t")

        try:
            family = data[0]
            domain = data[1]
            species = data[2]
            gene = data[3]

            data_dict["family"] = family
            data_dict["domain"] = domain
            data_dict["species"] = species
            data_dict["genbank"] = gene
            data_dict["tag"] = tag
        except IndexError:
            # no data for this line
            continue

        data_list.append(data_dict)

    return data_list


def fetch_links(enzyme_class, family, subfamily):
    """
    Fetch link structure for an enzyme class.

    Parameters
    ----------
    enzyme_class : str
        Enzyme class to fetch links for.

    Returns
    -------
    page_list : list
        List of links to the pages.

    """

    main_class_link = f"http://www.cazy.org/{enzyme_class}.html"
    log.info(f"Fetching links for {enzyme_class}, url: {main_class_link}")
    family_list = fetch_families(main_class_link)

    # Filter by family
    if family:
        if subfamily:
            log.info(f"Only using links of family {family} subfamily {subfamily}")
            family_list = [e for e in family_list if e[2:] == f"{family}_{subfamily}"]
        else:
            log.info(f"Only using links of family {family}")
            family_list = [e for e in family_list if int(e[2:]) == family]

    if not family_list:
        log.error("No links were found.")
        sys.exit()

    page_list = []
    for j, family in enumerate(family_list):
        # bar.update(j + 1)
        family_link = f"http://www.cazy.org/{family}.html"

        # TODO: Implement checkpoint for link fetching

        family_soup = BeautifulSoup(
            urllib.request.urlopen(family_link), features="html.parser"
        )

        # Find the links to the individual pages
        superfamily_links = []
        for line in family_soup.findAll("span", attrs={"class": "choix"}):
            _link = line.find("a")["href"]
            if "krona" not in _link and "structure" not in _link:
                superfamily_links.append(_link)

        for link in superfamily_links:
            page_zero = link
            try:
                soup = BeautifulSoup(
                    urllib.request.urlopen(link), features="html.parser"
                )
            except ValueError:
                # This is a link to a text file
                page_list.append(f"http://www.cazy.org/{link}")
                continue

            # Get page list for the family
            page_index_list = soup.findAll(name="a", attrs={"class": "lien_pagination"})
            if bool(page_index_list):
                # =====================#
                # be careful with this #
                first_page_idx = int(re.findall(r"=(\d*)#", str(page_index_list[0]))[0])
                last_page_idx = int(re.findall(r"=(\d*)#", str(page_index_list[-2]))[0])
                # =====================#

                page_list.append(page_zero)
                page_range = range(
                    first_page_idx, last_page_idx + first_page_idx, first_page_idx
                )
                for i in page_range:
                    sub_str = page_index_list[0]["href"].split("=")[0]
                    link = f"http://www.cazy.org/{sub_str}={i}"
                    page_list.append(link)

            else:
                page_list.append(page_zero)

    return page_list


def fetch_families(link):
    """
    Identify family link structure and return a list.

    Parameters
    ----------
    link : str
        Link to the page.

    Returns
    -------
    family_link_list : list
        List of family links.

    """
    enzyme_regex = r"([A-Z]{2}\d*_?\d?).html"
    soup = BeautifulSoup(urllib.request.urlopen(link), features="html.parser")
    all_links = soup.find_all("a")
    family_link_list = []
    for link in all_links:
        try:
            href = re.findall(enzyme_regex, link.attrs["href"])[0]
            family_link_list.append(href)
        except (IndexError, KeyError):
            continue

    return list(set(family_link_list))


def fetch_species():
    """Gather species names and IDs (full genome only)."""
    log.info("> Gathering species with full genomes")
    # a = archea // b = bacteria // e = eukaryota // v = virus
    species_domain_list = ["a", "b", "e", "v"]
    species_dic = {}

    bar = init_bar()
    bar.max_value = len(string.ascii_uppercase) * len(species_domain_list)
    bar.start()

    counter = 0
    for domain in species_domain_list:
        for initial in string.ascii_uppercase:
            counter += 1
            bar.update(counter)
            link = f"http://www.cazy.org/{domain}{initial}.html"
            f = urllib.request.urlopen(link)
            species_list_hp = f.read().decode("utf-8")
            # parse webpage
            index_list = re.findall(
                rf'"http://www.cazy.org/{species_domain_list}(\d.*).html"'
                r' class="nav">(.*)</a>',
                species_list_hp,
            )
            for entry in index_list:
                index, species = entry
                try:
                    species_dic[species].append(index)
                except KeyError:
                    species_dic[species] = [index]
    bar.finish()

    # Double check to see which of the species codes are valid
    for j, species in enumerate(species_dic.keys()):
        entry_list = species_dic[species]
        if len(entry_list) > 1:
            # More than one entry for this species
            #  > This is (likely) a duplicate
            #  > Use the higher number, should be the newer page
            newer_entry = max([int(i.split("b")[-1]) for i in entry_list])
            selected_entry = "b%i" % newer_entry

            species_dic[species] = selected_entry
        else:
            species_dic[species] = species_dic[species][0]

    return species_dic


def retrieve_genbank_ids(enzyme_name, family=None, subfamily=None, characterized=None):
    """
    Retrieve genbank IDs for a given enzyme.

    Parameters
    ----------
    enzyme_name : str
        Enzyme name to retrieve genbank IDs for.
    family : int
        Family number to retrieve genbank IDs for.
    subfamily : int
        Subfamily number to retrieve genbank IDs for.
    characterized : bool
        Whether to retrieve genbank IDs for characterized enzymes.

    Returns
    -------
    genbank_id_list : list
        List of genbank IDs.

    """
    page_list = fetch_links(enzyme_name, family, subfamily)
    data = fetch_data(page_list)
    genbank_id_list = []
    for element in data:
        if "genbank" in element:
            genbank_id_list.append(element["genbank"])

    return genbank_id_list
