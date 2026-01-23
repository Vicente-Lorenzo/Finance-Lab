import numpy as np
np.set_printoptions(threshold=1000, linewidth=1000)
import pandas as pd
pd.options.display.max_rows = None
pd.options.display.max_columns = None
pd.options.display.width = 0
pd.options.display.max_colwidth = None
import polars as pl
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_width_chars(1000)
pl.Config.set_fmt_str_lengths(1000)
pl.Config.set_fmt_table_cell_list_len(-1)

__all__ = [
    "np", "pd", "pl"
]
