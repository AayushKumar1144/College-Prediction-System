import pickle
from flask import Flask, request, render_template
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load the model
model = pickle.load(open("model1.pkl", "rb"))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')  

@app.route('/colleges')
def colleges():
    return render_template('Top Colleges.html')     

@app.route('/learn')
def learn():
    return render_template('Coding.html')     

@app.route('/support')
def support():
    return render_template('support.html')   

@app.route('/faq')
def faq():
    return render_template('faq.html')     

@app.route('/predict', methods=['POST'])
def predict():
    # Dictionaries for mapping form data to readable formats
    Category = {'0': 'General', '1': 'Other Backward Classes-Non Creamy Layer', '6': 'Scheduled Castes', '8': 'Scheduled Tribes',
                '3': 'General & Persons with Disabilities', '5': 'Other Backward Classes & Persons with Disabilities', 
                '7': 'Scheduled Castes & Persons with Disabilities', '9': 'Scheduled Tribes & Persons with Disabilities',
                '1': 'General & Economically Weaker Section', '2': 'General & Economically Weaker Section & Persons with Disability'}
    
    Quota = {'0': 'All-India', '3': 'Home-State', '1': 'Andhra Pradesh', '2': 'Goa', '4': 'Jammu & Kashmir', '5': 'Ladakh'}
    Pool = {'0': 'Neutral', '1': 'Female Only'}
    Institute = {'0': 'IIT', '1': 'NIT'}

    # Retrieve form data
    data = [x for x in request.form.values()]
    list1 = data.copy()

    # Validate the form inputs to prevent invalid data
    if 'Select your Category' in list1:
        return render_template("home.html", prediction_text="Please select a valid category.")

    # Convert form codes to readable format
    list1[2] = Category.get(list1[2], 'Unknown')  # Use 'Unknown' if invalid category
    list1[3] = Quota.get(list1[3], 'Unknown')  # Use 'Unknown' if invalid quota
    list1[4] = Pool.get(list1[4], 'Unknown')  # Use 'Unknown' if invalid pool
    list1[5] = Institute.get(list1[5], 'Unknown')  # Use 'Unknown' if invalid institute

    # Prepare data for prediction, ensure numeric data only
    data.pop(0)  # Adjust based on your form structure
    data.pop(0)
    data.pop(7)  # Adjust based on your form structure

    # Validate numeric data before conversion to float
    try:
        data1 = [float(x) if x not in ['Select your Category', 'Select your Quota', 'Select your Institute', 'Select your Pool'] else 0 for x in data]
    except ValueError as e:
        return render_template("home.html", prediction_text="Error: Invalid data entered, please check your inputs.")

    final_output = np.array(data1).reshape(1, -1)

    # Make prediction
    output = model.predict(final_output)[0]

    # Append prediction results to the list
    list1.extend([output[0], output[1], output[2]])

    # Load the original dataset (the one used for training)
    csv_file = "iit-and-nit-colleges-admission-criteria-version-2.csv"
    df = pd.read_csv(csv_file)

    # Debugging: Check form data length vs columns
    print("Form data length:", len(list1))
    print("Dataset columns length:", len(df.columns))
    
    # Ensure that the 'Unnamed: 0' column exists before dropping
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'], axis=1)

    print("Form data:", list1)
    print("Dataset columns:", df.columns)

    # Ensure list1 matches columns in csv_file
    if len(list1) != len(df.columns):
        return render_template("home.html", prediction_text="Column mismatch: please check the number of columns in the form data.")

    # Append the new row to the original dataset
    new_row = pd.DataFrame([list1], columns=df.columns)

    # Append the new row to the dataset
    df = pd.concat([df, new_row], ignore_index=True)

    # Save the updated dataset back to the CSV file
    df.to_csv(csv_file, index=False)

    # Return the prediction to the user
    return render_template("home.html", prediction_text="College: {} , Degree: {} , Course: {}".format(output[0], output[1], output[2]), prediction="Thank you, hope this meets your requirements!")

if __name__ == '__main__':
    app.run(debug=True)
