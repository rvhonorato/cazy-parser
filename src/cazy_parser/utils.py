import logging

import progressbar

log = logging.getLogger("cazylog")


def init_bar():
    """Initilize progress bar."""
    bar = progressbar.ProgressBar(
        widgets=[
            " ",
            progressbar.Timer(),
            " ",
            progressbar.Percentage(),
            " ",
            progressbar.Bar("█", "[", "]"),
            " ",
            progressbar.ETA(),
            " ",
        ]
    )
    return bar
