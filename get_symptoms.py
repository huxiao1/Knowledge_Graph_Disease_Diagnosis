'''
Topic:
    Extract patient symptoms using ChatGPT or manual input.

Usage:
    Two options are available:
    1. Provide the path to a text file containing the patient description and an API key.
        `python get_symptoms.py --input patient_description.txt --output symptoms.txt --api YOUR_API_KEY`
    2. Choose not to provide an API key and directly input symptoms in a single line.
        `python get_symptoms.py --output symptoms.txt`
        The script will prompt you to enter all symptoms in one line, separated by commas.

Input Format:
    - When using ChatGPT:
        `cat patient_description.txt`
        The patient is experiencing severe abdominal pain, nausea, and vomiting. 
        They also report occasional heartburn and difficulty swallowing.

    - When manually entering:
        The doctor will input a single line of symptoms separated by commas.
        Example:
        severe abdominal pain, nausea, vomiting, occasional heartburn, difficulty swallowing

Output Format:
    Extracted Symptoms: ['severe abdominal pain', 'nausea', 'vomiting', 'occasional heartburn', 'difficulty swallowing']
    Symptoms have been saved to symptoms.txt

    `cat symptoms.txt`
    severe abdominal pain
    nausea
    vomiting
    occasional heartburn
    difficulty swallowing
'''

import os
# set the number of threads to 1 for better performance cuz purdue server sucks!
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import openai
import argparse
import sys

def extract_symptoms(patient_description, api_key):
    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Ensure this is the correct model ID for your chat model
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced medical assistant. List the key symptoms the patient is experiencing based on the description below."
                },
                {
                    "role": "user",
                    "content": f"Patient Description:\n{patient_description}"
                }
            ],
            max_tokens=150,
            temperature=0.3,
            n=1,
            stop=None,
        )

        # Extract the symptoms from the response
        symptoms_text = response['choices'][0]['message']['content'].strip()

        # Parse the formatted response to extract just the symptoms
        symptoms_list = []
        for line in symptoms_text.split('\n'):
            line = line.strip()
            if line and line[0].isdigit():  # Checks if the line starts with a digit (e.g., "1.")
                # Splits the line at the first period and takes the part after the space, assuming the format "1. Symptom"
                symptom = line.split('. ', 1)[1].strip().lower()
                symptoms_list.append(symptom)

        return symptoms_list

    except Exception as e:
        print(f"Error communicating with OpenAI API: {e}")
        return []

def manual_input_symptoms():
    print("Please enter all symptoms you get from ChatGPT in one line, separated by commas.")
    print("Example Format: severe abdominal pain, nausea, vomiting, occasional heartburn, difficulty swallowing")
    symptom_line = input("Enter Symptoms: ").strip().lower()
    if not symptom_line:
        return []
    # Split the input line by commas and strip whitespace
    symptoms = [symptom.strip() for symptom in symptom_line.split(',') if symptom.strip()]
    return symptoms

def save_symptoms(symptoms, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for symptom in symptoms:
                f.write(symptom + '\n')
        print(f"Symptoms have been saved to {output_path}")
    except Exception as e:
        print(f"Error writing to file {output_path}: {e}")

def load_patient_description(input_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            patient_description = f.read()
        return patient_description
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{input_path}': {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Stage 1: Extract Symptoms from Patient Description")
    parser.add_argument('--input', type=str, help='Path to the input file containing patient description')
    parser.add_argument('--output', type=str, default='symptoms.txt', help='Path to the output symptoms file')
    parser.add_argument('--api', type=str, help='OpenAI API key. If not provided, symptoms will be input manually.')
    args = parser.parse_args()

    # Determine API key
    api_key = args.api if args.api else os.getenv('OPENAI_API_KEY')

    if api_key:
        # Use ChatGPT to extract symptoms
        # Read the patient description
        if args.input:
            patient_description = load_patient_description(args.input)
        else:
            print("Please enter the patient's description (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            patient_description = "\n".join(lines)

        if not patient_description.strip():
            print("Error: No patient description provided.")
            sys.exit(1)

        # Extract symptoms from the patient description
        symptoms = extract_symptoms(patient_description, api_key)
        if symptoms:
            print(f"\nExtracted Symptoms: {symptoms}")
            save_symptoms(symptoms, args.output)
        else:
            print("No symptoms were extracted.")
            sys.exit(1)
    else:
        # Manual input of symptoms in a single line
        print("\nNo API key provided. Please enter symptoms manually.")
        symptoms = manual_input_symptoms()
        if symptoms:
            print(f"\nEntered Symptoms: {symptoms}")
            save_symptoms(symptoms, args.output)
        else:
            print("No symptoms were entered.")
            sys.exit(1)

if __name__ == "__main__":
    main()
