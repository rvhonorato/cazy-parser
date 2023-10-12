import urllib.request

import pytest
from bs4 import BeautifulSoup

from cazy_parser.modules.html import (
    fetch_data,
    fetch_families,
    fetch_links,
    fetch_species,
    get_data_from_html,
    get_data_from_txt,
    parse_table,
    parse_td,
    retrieve_genbank_ids,
)


@pytest.fixture
def soup():
    soup = BeautifulSoup(
        urllib.request.urlopen("http://www.cazy.org/GH173_characterized.html"),
        features="html.parser",
    )
    return soup


@pytest.fixture
def table(soup):
    return soup.find("table", attrs={"class": "listing"})


@pytest.fixture
def td_list(table):
    td_list = [tr.findAll("td") for tr in table.findAll("tr")][3]
    return td_list


def test_fetch_data():
    observed_data = fetch_data(
        [
            "http://www.cazy.org/GH173_characterized.html",
            "http://www.cazy.org/IMG/cazy_data/GH173.txt",
        ]
    )

    assert [e for e in observed_data if "tag" in e]
    assert [e for e in observed_data if "family" in e]


def test_parse_td(td_list):
    observed_data_dic = parse_td(td_list)

    assert "protein_name" in observed_data_dic
    assert "pdb" in observed_data_dic
    assert "ec" in observed_data_dic


def test_parse_table(table):
    observed_data = parse_table(table)

    assert [e for e in observed_data if "protein_name" in e]


def test_get_data_from_html():
    observed_data = get_data_from_html(
        "http://www.cazy.org/GH173" "_characterized.html"
    )

    assert observed_data
    assert [e for e in observed_data if "protein_name" in e]


def test_get_data_from_txt():
    observed_data = get_data_from_txt("http://www.cazy.org/IMG/cazy_data/GH173.txt")

    assert [e for e in observed_data if "family" in e]


def test_fetch_links():
    observed_links = fetch_links("Carbohydrate-Esterases", characterized=True)

    assert "http://www.cazy.org/CE20_characterized.html" in observed_links
    assert "http://www.cazy.org/IMG/cazy_data/CE20.txt" not in observed_links

    observed_links = fetch_links("Carbohydrate-Esterases", characterized=False)

    assert "http://www.cazy.org/CE20_characterized.html" in observed_links
    assert "http://www.cazy.org/IMG/cazy_data/CE20.txt" in observed_links


def test_fetch_families():
    observed_families = fetch_families("http://www.cazy.org/Glycoside-Hydrolases.html")

    assert "GH1" in observed_families


def test_fetch_species():
    observed_species = fetch_species()

    assert observed_species
    assert isinstance(observed_species, dict)


def test_retrieve_genbank_ids():
    observed_id_list = retrieve_genbank_ids(
        enzyme_name="Glycoside-Hydrolases", family=5, subfamily=1, characterized=False
    )

    assert observed_id_list
    assert len(observed_id_list) >= 1223

    observed_id_list = retrieve_genbank_ids(
        enzyme_name="Glycoside-Hydrolases", family=5, subfamily=1, characterized=True
    )

    assert observed_id_list
    assert 36 <= len(observed_id_list) <= 1000
