#!/bin/bash

set -euox pipefail

MODEL_VERSION="master"
MODEL_VARIANT="candidate"
NUMBER_OF_TESTS="50"

CANDIDATE_MODEL_SHA="$(git rev-parse HEAD)"

make tag-push-local

make tag-push-master

env TARGET=master docker-compose --file docker/docker-compose.yml pull

env TARGET=master SERVER_PORT=5000 docker-compose --project-name master --file docker/docker-compose-ci-master.yml up --no-recreate -d ml_api
env TARGET=$CANDIDATE_MODEL_SHA SERVER_PORT=5001 docker-compose --project-name head --file docker/docker-compose-ci-candidate.yml up --no-recreate -d ml_api

env TARGET=master docker-compose --project-name master --file docker/docker-compose-ci-master.yml run -d --name differential-tests-expected differential-tests sleep infinity
env TARGET=$CANDIDATE_MODEL_SHA docker-compose --project-name head --file docker/docker-compose-ci-candidate.yml run -d --name differential-tests-actual differential-tests sleep infinity

docker ps --all

echo "===== Running $CANDIDATE_MODEL_SHA ... ====="

docker exec --user root differential-tests-actual \
    python3 differential_tests compute sample_payloads differential_tests/actual_results --base-url http://head_ml_api_1:5001


docker cp differential-tests-actual:/opt/app/differential_tests/actual_results/. differential_tests/actual_results

echo "===== Running master ... ====="

docker exec --user root differential-tests-expected \
    python3 differential_tests compute sample_payloads differential_tests/expected_results --base-url http://master_ml_api_1:5000

docker cp differential-tests-expected:/opt/app/differential_tests/expected_results/. differential_tests/expected_results

docker cp differential_tests/expected_results/. differential-tests-actual:/opt/app/differential_tests/expected_results

echo "===== Comparing $CANDIDATE_MODEL_SHA vs. master ... ====="

docker exec differential-tests-actual \
    python3 -m differential_tests compare differential_tests/expected_results differential_tests/actual_results

docker rm $(docker ps -a -q) -f
