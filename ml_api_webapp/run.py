import os
import uuid
import bcrypt
import requests
import pandas as pd
from api.app import create_app
from api.config import DevelopmentConfig, setup_app_logging
from flask import render_template, request, redirect, url_for, flash, send_file
# import prometheus_client
# from werkzeug.middleware.dispatcher import DispatcherMiddleware
_config = DevelopmentConfig()
LOCAL_URL = f'http://{os.getenv("DB_HOST", "localhost")}:5000'
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Base directory of your Flask app
upp = os.path.join(BASE_DIR, 'uploads') # app.config['UPLOAD_FOLDER']
pro = os.path.join(BASE_DIR, 'processed') # app.config['PROCESSED_FOLDER']

# Ensure the directories exist
if not os.path.exists(upp):
    os.makedirs(upp)

if not os.path.exists(pro):
    os.makedirs(pro)


# setup logging as early as possible
setup_app_logging(config=_config)
app = create_app(config_object=_config).app
app.secret_key = os.urandom(24)
# application = DispatcherMiddleware(app=main_app.wsgi_app,
#                                    mounts={'/metrics': prometheus_client.make_wsgi_app()}
#                                    )
# Home route for login
@app.route('/login_page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # user = User.query.filter_by(username=username, email=email).first() #in progress
        # if bcrypt.checkpw(entered_password.encode('utf-8'), hashed_password):
        #     print("Password matches")
        # else:
        #     print("Password does not match")

        user = True

        if user:
            return redirect(url_for('predict_lp'))
        else:
            flash('User not found, please register')
            return render_template('login_page.html')

    return render_template('login_page.html')

# Prediction page route
@app.route('/predict_lp', methods=['GET', 'POST'])
def predict_lp():
    if request.method == 'POST':
        if 'file' not in request.files: # post==sumbit thus we must have uploaded the file otherwise 'No file ...'
            flash('No file path')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '': # here file path but no file name
            flash('No selected file')
            return redirect(request.url)

        if file:
            file_path = os.path.join(upp, file.filename)
            file.save(file_path) # if file is selected then we save first

            # then we determine the file extension and read into a DataFrame
            if file.filename.endswith('.csv'):
                df_input = pd.read_csv(file_path, decimal=',')
            elif file.filename.endswith('.json'):
                df_input = pd.read_json(file_path)
            else:
                flash('Unsupported file format, only .csv or .json files')
                return redirect(request.url)

            # Make the API call to /v1/predictions with the file content

            predictions = []
            for index, data in df_input.iterrows():
                response = requests.post("http://localhost:5000/v1/predictions",
                                        headers=HEADERS,
                                        json=[data.to_dict()])
                response.raise_for_status()

                json_data = response.json()
                predictions.append(json_data.get('predictions'))
            df_input['model_predictions'] =  sum(predictions, [])

            # Save the processed DataFrame to a new file
            processed_filename = f'processed_{file.filename}'
            processed_file_path = os.path.join(pro, processed_filename)

            if file.filename.endswith('.csv'):
                df_input.to_csv(processed_file_path, index=False)
            elif file.filename.endswith('.json'):
                df_input.to_json(processed_file_path, orient='records')

            # Flash a message indicating the file is ready for download
            flash(f'File processed and ready for download: {processed_filename}')
            return redirect(f'/predict_lp?filename={processed_filename}')

    return render_template('predict_lp.html')


@app.route('/download')
def download_file():
    filename = request.args.get('filename')
    if not filename:
        flash('No file specified for download')
        return redirect('/predict_lp')
    # here we
    file_path = os.path.join(pro, filename)
    if os.path.exists(file_path):
        response = send_file(file_path, as_attachment=True)
        os.remove(file_path)
        flash('File downloaded and deleted from the system')
        return response
    else:
        flash('File not found')
        return redirect('/predict_lp')


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        user = False
        if user: # User.query.filter_by(email=email).first():
            flash('Email already registered.')

        else:
            user_id = uuid.uuid4()
            password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            data = {'user_id': str(user_id), 'username': username, 'email': email, 'password': password}
            response = requests.post("http://localhost:5000/v1/registration",
                                     headers=HEADERS,
                                     json=[data])
            response.raise_for_status()

            flash('Registration successful! Please log in.')
            return redirect(url_for('login_page'))

    return render_template('register.html')


if __name__ == "__main__":
    app.run(port=_config.SERVER_PORT, host=_config.SERVER_HOST)
