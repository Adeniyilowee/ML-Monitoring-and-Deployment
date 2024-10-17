from unittest import mock
import pytest

from api.persistence.data_access import PredictionPersistence, ModelType

from api.persistence.models import BaggingModelPredictions, BoostingModelPredictions


@pytest.mark.parametrize(
    "model_type, model",
    (
        (ModelType.BOOSTING, BoostingModelPredictions),
        (ModelType.BAGGING, BaggingModelPredictions),
    ),
)
def test_data_access(model_type, model, test_inputs_df):
    # Given
    # We mock the database session
    mock_session = mock.MagicMock()
    _persistence = PredictionPersistence(db_session=mock_session)

    # When
    _persistence.make_save_predictions(db_model=model_type, input_data=test_inputs_df.to_dict(orient="records"))

    # Then
    assert mock_session.commit.call_count == 1
    assert mock_session.add.call_count == 1
    assert isinstance(mock_session.add.call_args[0][0], model)
