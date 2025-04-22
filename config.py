import pandas as pd
CLIENT_ID = ""
CLIENT_SECRET = ""
DF_PATH = "data/TRACK_NAME.csv"
DF_AFTER_OPERATION_PATH = "data/TRACK_SAVE_PATH.csv"
VERBOSE = True
EXTRA_VERBOSE = VERBOSE and False
# Should we sample the dataset (reduces time)? If so, what values should we cutoff the sample with and what column are they found in?
SAMPLE, SAMPLE_CUTOFF, SAMPLE_COLUMN = True, "2008-01-01", "release_date"
# global pd config
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)