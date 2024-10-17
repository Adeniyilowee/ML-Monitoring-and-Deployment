import logging
import connexion
from api.config import Config
# --- SM
from api.persistence.core import init_database
from sqlalchemy.orm import scoped_session

_logger = logging.getLogger('mlapi')


def create_app(*, config_object: Config, db_session: scoped_session = None) -> connexion.App:
    """Create app instance."""

    connexion_app = connexion.App(__name__,
                                  debug=config_object.DEBUG,
                                  specification_dir="spec/")
    flask_app = connexion_app.app
    flask_app.config.from_object(config_object)

    init_database(flask_app, config=config_object, db_session=db_session)

    connexion_app.add_api("api.yaml")
    _logger.info("Application instance created")

    return connexion_app
