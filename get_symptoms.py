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

import openai
import os
import argparse
import sys

def extract_symptoms(patient_description, api_key):
    openai.api_key = api_key

    # Prompt for ChatGPT
    prompt = f"""
    You are an experienced medical assistant. Based on the patient's description provided below, extract the key symptoms that the patient is experiencing. Please list the symptoms as a comma-separated list in English.

    Patient Description:
    {patient_description}

    Extracted Symptoms:
    """

    try:
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=150,
            temperature=0.3,
            n=1,
            stop=None,
        )

        # Extract the symptoms from the response
        symptoms_text = response.choices[0].text.strip()
        symptoms_list = [symptom.strip().lower() for symptom in symptoms_text.split(',') if symptom.strip()]

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
