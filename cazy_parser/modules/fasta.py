import logging
import os

from Bio import Entrez, SeqIO

Entrez.email = "your-email-here@example.org"

log = logging.getLogger("cazylog")


def download_fastas(id_list):
    """
    Download fasta files from NCBI.

    Parameters
    ----------
    id_list : list
        List of genbank ids.

    Returns
    -------
    fasta_list : list
        List of fasta strings.

    """
    log.info(f"Dowloading {len(id_list)} fasta sequences...")
    fasta_list = []
    handle = Entrez.efetch(db="protein", id=id_list, rettype="fasta", retmode="text")
    for seq_record in SeqIO.parse(handle, "fasta"):
        fasta_str = (
            f">{seq_record.description}{os.linesep}" f"{seq_record.seq}{os.linesep*2}"
        )
        fasta_list.append(fasta_str)

    return fasta_list


def dump_fastas(id_list, output_f):
    """
    Save the fasta strings to a file.

    Parameters
    ----------
    id_list : list
        List of genbank ids.
    output_f : str
        Path to the output file.

    """
    fasta_list = download_fastas(id_list)
    log.info(f"Dumping fasta sequences to file {output_f}")
    with open(output_f, "w") as fh:
        for fasta in fasta_list:
            fh.write(fasta)
