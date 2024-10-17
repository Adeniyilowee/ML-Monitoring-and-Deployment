from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from api.persistence.core import Base


class BaggingModelPredictions(Base):
    __tablename__ = "bagging_model_predictions"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), nullable=False)
    datetime_captured = Column(DateTime(timezone=True),
                               server_default=func.now(),
                               index=True)

    model_version = Column(String(36), nullable=False)
    inputs = Column(JSONB)
    outputs = Column(JSONB)


class BoostingModelPredictions(Base):
    __tablename__ = "boosting_model_predictions"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), nullable=False)
    datetime_captured = Column(DateTime(timezone=True),
                               server_default=func.now(),
                               index=True)

    model_version = Column(String(36), nullable=False)
    inputs = Column(JSONB)
    outputs = Column(JSONB)


class Users(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(120), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    datetime_captured = Column(DateTime(timezone=True),
                                server_default=func.now(),
                                index=True)
