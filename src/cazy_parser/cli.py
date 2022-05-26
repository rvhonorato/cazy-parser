import argparse
import logging
import sys
import time

from cazy_parser import ENZYME_LIST
from cazy_parser.modules.fasta import dump_fastas
from cazy_parser.modules.html import retrieve_genbank_ids
from cazy_parser.version import VERSION

log = logging.getLogger("cazylog")
ch = logging.StreamHandler()
formatter = logging.Formatter(" [%(asctime)s %(lineno)d %(levelname)s] %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)
log.setLevel("DEBUG")


# CONFIG = json.load(open(Path(Path(__file__).parents[2], "etc/config.json")))

# ===========================================================================================================
# Define arguments
ap = argparse.ArgumentParser()

ap.add_argument(
    "enzyme_class",
    choices=["GH", "GT", "PL", "CA", "AA"],
)

ap.add_argument("-f", "--family", type=int)

ap.add_argument("-s", "--subfamily")

ap.add_argument("-c", "--characterized")

ap.add_argument(
    "-v",
    "--version",
    help="show version",
    action="version",
    version=f"Running {ap.prog} v{VERSION}",
)


def load_args(ap):
    """
    Load argument parser.

    Parameters
    ----------
    ap : argparse.ArgumentParser
        Argument parser.

    Returns
    -------
    cmd : argparse.Namespace
        Parsed command-line arguments.

    """
    return ap.parse_args()


# ====================================================================================#
# Define CLI
def cli(ap, main):
    """
    Command-line interface entry point.

    Parameters
    ----------
    ap : argparse.ArgumentParser
        Argument parser.
    main : function
        Main function.

    """
    cmd = load_args(ap)
    main(**vars(cmd))


def maincli():
    """Execute main client."""
    cli(ap, main)


# ====================================================================================#
# Main code
def main(enzyme_class, family, subfamily, characterized):
    """Main function."""

    log.info("-" * 42)
    log.info("")
    log.info("┌─┐┌─┐┌─┐┬ ┬   ┌─┐┌─┐┬─┐┌─┐┌─┐┬─┐")
    log.info("│  ├─┤┌─┘└┬┘───├─┘├─┤├┬┘└─┐├┤ ├┬┘")
    log.info(f"└─┘┴ ┴└─┘ ┴    ┴  ┴ ┴┴└─└─┘└─┘┴└─ v{VERSION}")
    log.info("")
    log.info("-" * 42)

    if enzyme_class not in ENZYME_LIST:
        logging.error(f"Enzyme class {enzyme_class} not supportes")
        sys.exit()
    else:
        enzyme_name = ENZYME_LIST[enzyme_class]

    id_list = retrieve_genbank_ids(enzyme_name, family, subfamily, characterized)

    output_fname = f"{enzyme_class}"
    if family:
        output_fname += f"{family}"
    if subfamily:
        output_fname += f"_{subfamily}"

    today = time.strftime("%d%m%Y")
    output_fname += f"_{today}.fasta"
    dump_fastas(id_list, output_fname)


if __name__ == "__main__":
    sys.exit(maincli())
