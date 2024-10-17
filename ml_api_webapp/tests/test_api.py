import json
import time
import pytest
from lspb_model.processing.data_management import load_testdataset
from lsp_model.processing.data_management import load_testdataset as load_testdatasetb
from api.persistence.models import BoostingModelPredictions, BaggingModelPredictions


@pytest.mark.integration  # the integration here is a marker to indicate what test we want to run
def test_health_endpoint(client):

    #  this is how we query the api from code
    #  this code can be inserted within an HTML web design to determine its location
    response = client.get("/")

    # Then
    assert response.status_code == 200
    assert json.loads(response.data) == {"status": "ok"}


@pytest.mark.integration
def test_prediction_endpoint(client):
    # Given
    # Load the test dataset which is included in the model package
    test_inputs_df = load_testdataset(file_name="validation1.csv")  # dataframe
    test_inputs_df = test_inputs_df.copy()
    expected_output_length = 10
    # this is how we query the api from code
    # this code can be inserted within an HTML web design to determine its location
    response = client.post("/v1/predictions/boosting", json=test_inputs_df.to_dict(orient="records"))

    # Then
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["errors"] is None
    assert len(data["predictions"]) == expected_output_length


# parameterizationa allows us to try many combinations of data
# within the same test, see the pytest docs for details:
# https://docs.pytest.org/en/latest/parametrize.html
@pytest.mark.parametrize(
    "field, field_value, index, expected_error",
    (
        (
            "STREAM_DIST",  # model feature
            "abc",  # expected float
            4,
            {"4": {"STREAM_DIST": ["Not a valid number."]}},
        ),
        (
            "SCARPS",
            "",
            2,
            {"2": {"SCARPS": ["Not a valid integer."]}},
        ),
    ),
)
@pytest.mark.integration
def test_prediction_validation(field, field_value, index, expected_error, client):
    # Given
    # Load the test dataset which is included in the model package
    test_inputs_df = load_testdataset(file_name="validation1.csv")  # dataframe
    test_inputs_df = test_inputs_df.copy()
    # Check lsp_model.processing.validation import LandslideSchema
    # and you will see the expected values for the inputs to the landslide prediction
    # model. In this test, inputs are changed to incorrect values to check the validation.
    test_inputs_df.loc[index, field] = field_value

    # When
    response = client.post("/v1/predictions/boosting", json=test_inputs_df.to_dict(orient="records"))

    # Then
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data == expected_error


# Though it is an integration marker but possible due to differential setup
@pytest.mark.integration
@pytest.mark.parametrize(
    "api_endpoint, expected_no_predictions",
    (
        (
            "v1/predictions/bagging",
            10,
        ),
        (
            "v1/predictions/boosting",
            10,
        ),
    ),
)
def test_prediction_endpoint_2(api_endpoint, expected_no_predictions, client):

    # Load the test dataset which is included in the model package
    if api_endpoint == "v1/predictions/bagging":
        test_inputs_df = load_testdatasetb(file_name="validation1.csv")  # dataframe

    elif api_endpoint == "v1/predictions/boosting":
        test_inputs_df = load_testdataset(file_name="validation1.csv")  # dataframe

    response = client.post(api_endpoint, json=test_inputs_df.to_dict(orient="records"))

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["errors"] is None
    assert len(data["predictions"]) == expected_no_predictions


@pytest.mark.integration
def test_prediction_data_saved(client, app, test_inputs_df):
    # Given
    boosting_record_count = app.db_session.query(BoostingModelPredictions).count()
    bagging_record_count = app.db_session.query(BaggingModelPredictions).count()

    # When
    response = client.post("/v1/predictions", json=test_inputs_df.to_dict(orient="records"))

    # Then
    assert response.status_code == 200
    assert app.db_session.query(BoostingModelPredictions).count() == boosting_record_count + 1
    time.sleep(2)
    assert app.db_session.query(BaggingModelPredictions).count() == bagging_record_count + 1
