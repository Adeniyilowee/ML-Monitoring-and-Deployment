import json
import logging
import threading

from flask import request, jsonify, Response
from lspb_model.predict import make_prediction

from lsp_model.predict import make_prediction as make_prediction_bagging

from flask import current_app
from api.persistence.data_access import PredictionPersistence, ModelType, Users_persistence


_logger = logging.getLogger('mlapi')

def health():
    if request.method == "GET":
        status = {"status": "ok"}
        _logger.debug(status)
        return jsonify(status)



def predict_oldmodel():
    if request.method == "POST":
        json_data = request.get_json()

        result = make_prediction(test_data=json_data)

        errors = result.get("errors")
        if errors:
            return Response(json.dumps(errors), status=400)

        predictions = result.get("predictions").tolist()
        version = result.get("version")

        return jsonify({"predictions": predictions, "version": version, "errors": errors})


def predict_newmodel():
    if request.method == "POST":
        json_data = request.get_json()

        result = make_prediction_bagging(test_data=json_data)

        errors = result.get("errors")
        if errors:
            return Response(json.dumps(errors), status=400)

        predictions = result.get("predictions").tolist()
        version = result.get("version")

        persistence = PredictionPersistence(db_session=current_app.db_session)
        persistence.save_predictions(inputs=json_data,
                                     model_version=version,
                                     predictions=predictions,
                                     db_model=ModelType.BAGGING)

        return jsonify({"predictions": predictions, "version": version, "errors": errors})


def predict():
    if request.method == "POST":
        json_data = request.get_json()

        persistence = PredictionPersistence(db_session=current_app.db_session)
        result = persistence.make_save_predictions(db_model=ModelType.BOOSTING,
                                                   input_data=json_data)

        if current_app.config.get("SHADOW_MODE_ACTIVE"):
            _logger.debug(f"Calling shadow model asynchronously: " f"{ModelType.BAGGING.value}")
            thread = threading.Thread(target=persistence.make_save_predictions,
                                      kwargs={"db_model": ModelType.BAGGING,
                                              "input_data": json_data})
            thread.start()

        if result.errors:
            _logger.warning(f"errors during prediction: {result.errors}")
            return Response(json.dumps(result.errors), status=400)

        return jsonify({"predictions": result.predictions, "version": result.model_version, "errors": result.errors})

def registration():
    if request.method == "POST":

        json_data = request.get_json()
        json_data = json_data[0]
        persistence = Users_persistence(db_session=current_app.db_session)
        persistence.save_users(user_id=json_data['user_id'],
                               username=json_data['username'],
                               email=json_data['email'],
                               password=json_data['password'])
