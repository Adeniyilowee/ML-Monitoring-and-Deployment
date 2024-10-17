import enum
import logging
import typing as t
import pandas as pd

from sqlalchemy.orm.session import Session
# for testing shadow mode
from lspb_model.predict import make_prediction as make_shadow_prediction
from lsp_model.predict import make_prediction as make_live_prediction

from api.persistence.models import BaggingModelPredictions, BoostingModelPredictions, Users

_logger = logging.getLogger(__name__)


class ModelType(enum.Enum):
    BAGGING = "bagging"
    BOOSTING = "boosting"


class PredictionResult(t.NamedTuple):
    errors: t.Any
    predictions: t.Any
    model_version: str


MODEL_PREDICTION_MAP = {
    ModelType.BOOSTING: make_shadow_prediction,
    ModelType.BAGGING: make_live_prediction
}


class PredictionPersistence:
    def __init__(self, *, db_session: Session, user_id: t.Optional[str] = None) -> None:
        self.db_session = db_session
        if not user_id:

            self.user_id = "007"

    def make_save_predictions(self,
                              *,
                              db_model: ModelType,
                              input_data) -> PredictionResult:

        """Get the prediction from a given model and persist it."""

        live_df = pd.DataFrame(input_data)

        result = MODEL_PREDICTION_MAP[db_model](test_data=live_df)
        errors = None
        try:
            errors = result["errors"]
        except KeyError:
            pass

        prediction_result = PredictionResult(errors=errors,
                                             predictions=result.get("predictions").tolist() if not errors else None,
                                             model_version=result.get("version"))

        if prediction_result.errors:
            return prediction_result

        self.save_predictions(inputs=input_data,
                              model_version=prediction_result.model_version,
                              predictions=prediction_result.predictions,
                              db_model=db_model)

        return prediction_result


    def save_predictions(self,
                         *,
                         inputs,
                         model_version,
                         predictions,
                         db_model: ModelType) -> None:

        if db_model == ModelType.BAGGING:
            prediction_data = BaggingModelPredictions(user_id=self.user_id,
                                                      model_version=model_version,
                                                      inputs=inputs,
                                                      outputs=predictions)
        else:
            prediction_data = BoostingModelPredictions(user_id=self.user_id,
                                                       model_version=model_version,
                                                       inputs=inputs,
                                                       outputs=predictions)

        self.db_session.add(prediction_data)
        self.db_session.commit()  # here the data is persist into the dataframe
        _logger.debug(f"saved data for model: {db_model}")


class Users_persistence:
    def __init__(self, *, db_session: Session) -> None:

        self.db_session = db_session


    def save_users(self,
                   *,
                   user_id: t.Optional[str] = None,
                   username: t.Optional[str] = None,
                   email: t.Optional[str] = None,
                   password: t.Optional[str] = None) -> None:

        user_data = Users(user_id=user_id,
                          username=username,
                          email=email,
                          password=password)

        self.db_session.add(user_data)
        self.db_session.commit()
        _logger.debug(f"saved data for users: {username}")
