from lspb_model.processing.data_management import load_testdataset
import requests
import pandas as pd

from random import randint
import os
import time
import random


LOCAL_URL = f'http://{os.getenv("DB_HOST", "localhost")}:5002'
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

STREAM_DIST	= {"min": 20.24, "max": 100.78}
CURVATURE = {"min": 8.24, "max": 12.78}
CURVE_CONT = {"min": 11.24, "max": 12.78}
DROP = {"min": 10.24, "max": 21.78}
SCARP_DIST = {"min": 0.24, "max": 113.78}
SLOPE = {"min": 8.24, "max": 42.78}
SPECIFIC_WT = {"min": 18.0, "max": 25.0}


def _generate_random_values(value, value_ranges):
    """Generate random values within a min and max range."""
    random_value = random.uniform(value_ranges["min"], value_ranges["max"])

    return random_value


def _prepare_inputs(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe.loc[:, "STREAM_DIST"] = dataframe["STREAM_DIST"].apply(_generate_random_values,
                                                                     value_ranges=STREAM_DIST)
    dataframe.loc[:, "CURVATURE"] = dataframe["CURVATURE"].apply(_generate_random_values,
                                                                 value_ranges=CURVATURE)
    dataframe.loc[:, "CURVE_CONT"] = dataframe["CURVE_CONT"].apply(_generate_random_values,
                                                                   value_ranges=CURVE_CONT)
    dataframe.loc[:, "DROP"] = dataframe["DROP"].apply(_generate_random_values,
                                                       value_ranges=DROP)
    dataframe.loc[:, "SCARP_DIST"] = dataframe["SCARP_DIST"].apply(_generate_random_values,
                                                                   value_ranges=SCARP_DIST)
    dataframe.loc[:, "SLOPE"] = dataframe["SLOPE"].apply(_generate_random_values,
                                                         value_ranges=SLOPE)
    dataframe.loc[:, "SPECIFIC_WT"] = dataframe["SPECIFIC_WT"].apply(_generate_random_values,
                                                                     value_ranges=SPECIFIC_WT)

    return dataframe


def populate_database(n_predictions: int = 500) -> None:
    """
    Manipulate the test data to generate random
    predictions and save them to the database.
    Before running this script, ensure that the
    API and Database docker containers are running.
    """

    print(f"Preparing to generate: {n_predictions} predictions.")
    inputs_df = load_testdataset(file_name="validation1.csv")
    edited_inputs_df = _prepare_inputs(dataframe=inputs_df)
    if len(edited_inputs_df) < n_predictions:
        print(f"If you want {n_predictions} predictions, you need to"
            "extend the script to handle more predictions.")

    for index, data in edited_inputs_df.iterrows():
        if index > n_predictions:
            break
 #       try:
        response = requests.post(f"{LOCAL_URL}/v1/predictions",
                                headers=HEADERS,
                                json=[data.to_dict()])

        response.raise_for_status()
 #       except requests.exceptions.RequestException as e:
 #           print(f"Failed to connect to the server: {e}")

        if index % 50 == 0:
            print(f"{index} predictions complete")

            # prevent overloading the server
            time.sleep(0.5)

    print("Prediction generation complete.")


if __name__ == "__main__":
    populate_database(n_predictions=500)
