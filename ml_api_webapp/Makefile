.PHONY: run-service-development

run-service-development:
	@echo "+ $@"
	python run.py


db-migrations:
	@echo "+ $@"
	PYTHONPATH=. alembic -c alembic.ini upgrade head
