# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


def eog_intervalrelated(data):
    """**EOG analysis on longer periods of data**

    Performs EOG analysis on longer periods of data (typically > 10 seconds), such as resting-state
    data.

    Parameters
    ----------
    data : Union[dict, pd.DataFrame]
        A DataFrame containing the different processed signal(s) as different columns, typically
        generated by :func:`.eog_process` or :func:`.bio_process`. Can also take a dict containing
        sets of separately processed DataFrames.

    Returns
    -------
    DataFrame
        A dataframe containing the analyzed EOG features. The analyzed features consist of the
        following:

        * ``"EOG_Rate_Mean"``: the mean heart rate.

        * ``"EOG_Peaks_N"``: the number of blink peak occurrences.

    See Also
    --------
    bio_process, eog_eventrelated

    Examples
    ----------
    .. ipython:: python

      import neurokit2 as nk

      # Download data
      eog = nk.data('eog_200hz')['vEOG']

      # Process the data
      df, info = nk.eog_process(eog, sampling_rate=200)

      # Single dataframe is passed
      nk.eog_intervalrelated(df)

      # Dictionary is passed
      epochs = nk.epochs_create(df, events=[0, 30000], sampling_rate=200,
                                epochs_end=120)
      nk.eog_intervalrelated(epochs)


    """
    intervals = {}

    # Format input
    if isinstance(data, pd.DataFrame):
        rate_cols = [col for col in data.columns if "EOG_Rate" in col]
        if len(rate_cols) == 1:
            intervals.update(_eog_intervalrelated_formatinput(data))

        eog_intervals = pd.DataFrame.from_dict(intervals, orient="index").T

    elif isinstance(data, dict):
        for index in data:
            intervals[index] = {}  # Initialize empty container

            # Add label info
            intervals[index]["Label"] = data[index]["Label"].iloc[0]

            # Rate and Blinks quantity
            intervals[index] = _eog_intervalrelated_formatinput(data[index], intervals[index])

        eog_intervals = pd.DataFrame.from_dict(intervals, orient="index")

    return eog_intervals


# =============================================================================
# Internals
# =============================================================================


def _eog_intervalrelated_formatinput(data, output={}):

    # Sanitize input
    colnames = data.columns.values
    if len([i for i in colnames if "EOG_Rate" in i]) == 0:
        raise ValueError(
            "NeuroKit error: eog_intervalrelated(): Wrong input,"
            "we couldn't extract EOG rate. Please make sure"
            "your DataFrame contains an `EOG_Rate` column."
        )
    if len([i for i in colnames if "EOG_Blinks" in i]) == 0:
        raise ValueError(
            "NeuroKit error: eog_intervalrelated(): Wrong input,"
            "we couldn't extract EOG blinks. Please make sure"
            "your DataFrame contains an `EOG_Blinks` column."
        )

    signal = data["EOG_Rate"].values
    n_blinks = len(np.where(data["EOG_Blinks"] == 1)[0])

    output["EOG_Peaks_N"] = n_blinks
    output["EOG_Rate_Mean"] = np.mean(signal)

    return output
