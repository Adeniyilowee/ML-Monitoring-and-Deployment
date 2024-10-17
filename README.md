# Landslide Prediction ML Model Service

This repository hosts a machine learning model service for landslide prediction. Users need to register and log in to access the prediction API. The frontend is built with **Flask**, **HTML**, and **CSS**, communicating with the backend using **Swagger OpenAPI**. **Docker** is used for deployment with multiple services for monitoring.

## Requirements
- Python 3.8+
- Docker
- PostgreSQL
- Flask
- Prometheus
- Grafana
- Kibana
- CAdvisor

## Setup Instructions

1. Clone the repository:
    ```bash
    git clone https://github.com/Adeniyilowee/ML-Monitoring-and-Deployment
    ```
2. Navigate to the cloned folder:
    ```bash
    cd ML-Monitoring-and-Deployment
    ```
3. Initialize submodules:
    ```bash
    git submodule update --init --recursive
    ```
4. Create a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
5. Install the web app locally:
    ```bash
    cd ml_api_webapp
    pip install .
    ```
6. Install the required dependencies:
    ```bash
    pip install -r requirements/requirements.txt
    ```

7. Copy submodels `bagging_model` and `boosting_model` to the `docker` folder.

8. Build and run the Docker containers:
    ```bash
    docker compose -f docker/docker-compose.yml up -d --build
    ```

9. Access the application:
    - API Swagger UI: [http://localhost:5000/ui](http://localhost:5000/ui)
    - Login Page: [http://localhost:5000/login_page](http://localhost:5000/login_page)

## Monitoring Tools
- **Grafana**, **Prometheus**, **Kibana**, and **CAdvisor** are used to monitor metrics and logs in Docker.

## Web Page Visualization

### Login Page
![Login](./images/login_page.png)

### Make Prediction Page
![Make Prediction](./images/make_prediction.png)

## To-Do
- Create user authentication linked to the database.
- Implement a registration API.
- Develop a dashboard for visualizing the predicted results.
