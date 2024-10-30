# Importing useful libraries

from dotenv import load_dotenv
import os
from functools import wraps
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, jsonify, session  
from PIL import Image
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.account import Account
from appwrite.id import ID


load_dotenv()
app = Flask(__name__)










client = Client()
(client
    .set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
    .set_project(os.getenv('APPWRITE_PROJECT_ID'))
    .set_key(os.getenv('APPWRITE_API_KEY'))
    .set_self_signed(True)
)
users = Users(client)



account = Account(client)

















app.secret_key = os.urandom(24)  

genai.configure(api_key=os.getenv('GENAI_API_KEY'))

def get_gemini_response(input_prompt, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, image[0]])
    return response.text

def input_image_setup(image_path):
    with open(image_path, "rb") as file:
        bytes_data = file.read()

    image_parts = [
        {
            "mime_type": "image/jpeg",
            "data": bytes_data
        }
    ]
    return image_parts

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:  # Check if user is in session
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            # Create a new user in Appwrite
            account.create(ID.unique(), email=email, password=password, name=name)
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('signup.html', error=str(e))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            # Pass email and password as positional arguments
            session_response = account.create_session(email, password)

            # Check if session creation was successful
            if session_response and session_response.get('$id'):
                session['user'] = email
                return redirect(url_for('index'))
            else:
                error_message = "Login failed: Invalid credentials."
                return render_template('login.html', error=error_message)

        except Exception as e:
            error_message = f"Login error: {str(e)}"
            return render_template('login.html', error=error_message)

    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)

        file = request.files['image']

        if file.filename == '':
            return redirect(request.url)

        image_path = 'static/' + file.filename
        file.save(image_path)

        input_prompt = """
        You are an expert nutritionist tasked with analyzing food items from an image. Your goal is to provide detailed nutritional information for each unique food item identified, including total calories and protein content. If there are multiple quantities of the same item, list the total quantity along with its nutritional information. Please present the information in the following format:

        **Food Items:**
        1. Item 1 (Quantity: [quantity]) - [calories] calories, [protein]g protein
        2. Item 2 (Quantity: [quantity]) - [calories] calories, [protein]g protein
        3. Item 3 (Quantity: [quantity]) - [calories] calories, [protein]g protein
        ----
        [Continue for additional unique items]

        **Disease Risks:**
        Please assess the potential health risks associated with these food items, considering factors such as high sugar, fat content, and other relevant nutritional information.

        **Health Assessment:**
        Based on the analysis, indicate whether the food items are considered healthy or unhealthy. Provide a brief explanation of your assessment.

        **Healthy Alternatives:**
        Suggest healthier alternatives to the identified food items in the following format:
        1. Alternative Item 1 (Quantity: [quantity]) - [calories] calories, [protein]g protein
        2. Alternative Item 2 (Quantity: [quantity]) - [calories] calories, [protein]g protein
        3. Alternative Item 3 (Quantity: [quantity]) - [calories] calories, [protein]g protein
        ----
        [Continue for additional alternatives]
        """

        image_data = input_image_setup(image_path)
        response = get_gemini_response(input_prompt, image_data)

        print(response)

        return jsonify(response=response)
    return render_template('index.html')








if __name__ == '__main__':
    app.run(debug=True)
