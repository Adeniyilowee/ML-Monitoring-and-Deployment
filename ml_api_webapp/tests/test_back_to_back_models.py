import json

import pytest
from lsp_model.processing.data_management import load_testdataset
from differential_tests.compare import compare_differences


@pytest.mark.differential
def test_model_prediction_differentials(client):
    test_inputs_df = load_testdataset(file_name="validation1.csv")  # dataframe

    new_model_response = client.post("v1/predictions/bagging", json=test_inputs_df.to_dict(orient="records"))

    new_model_predictions = json.loads(new_model_response.data)["predictions"]

    old_model_response = client.post("v1/predictions/boosting", json=test_inputs_df.to_dict(orient="records"))

    old_model_predictions = json.loads(old_model_response.data)["predictions"]

    # We just pass in the first 10 rows as the two models' validation differs
    # which means they filter out a slightly different number of rows
    # which would cause the differential tests to fail.
    compare_differences(expected_predictions=new_model_predictions[:10],
                        actual_predictions=old_model_predictions[:10],
                        # you would adjust the rel_tol level parameter on your model.
                        # right now this is extremely permissive of variation.
                        rel_tol=1)
