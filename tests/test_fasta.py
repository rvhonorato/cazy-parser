import tempfile
from pathlib import Path

import pytest

from cazy_parser.modules.fasta import download_fastas, dump_fastas


@pytest.fixture
def id_list():
    return ["WP_010249057.1", "ABN51772.1"]


def test_download_fastas(id_list):
    observed_fasta_list = download_fastas(id_list)

    assert len(observed_fasta_list) == 2
    assert observed_fasta_list[0][0] == ">"


def test_dump_fastas(id_list):
    temp_f = tempfile.NamedTemporaryFile(delete=False)
    dump_fastas(id_list, temp_f.name)

    assert Path(temp_f.name).exists()
    assert Path(temp_f.name).stat().st_size != 0
