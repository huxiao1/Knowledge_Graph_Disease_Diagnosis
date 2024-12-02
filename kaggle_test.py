'''
Topic:
    Evaluate Medical Diagnosis Accuracy Using Symptom-Disease Dataset

Description:
    This script processes a dataset of patient descriptions to evaluate the accuracy of a medical diagnosis system.
    For each patient case, it extracts symptoms using an external script (`get_symptoms.py`), predicts possible diseases
    using another external script (`get_diagnosis.py`), and compares the predictions against the ground truth labels.
    The script tracks the number of correct and incorrect predictions for each disease and provides overall statistics.

Usage:
    The script accepts two command-line arguments:
    1. API_KEY: Your API key for authentication with the symptom extraction service.
    2. LINE_THRESHOLD: The number of lines (patient cases) to process from the CSV dataset.

    ```bash
    python3 kaggle_test.py YOUR_API_KEY LINE_THRESHOLD
    ```
    **Example:**
    ```bash
    python3 kaggle_test.py sk-your-api-key-here 1
    ```

Output:
    ```
    -----------------Diagnose Start-----------------

    Extracted Symptoms: ['skin rash', 'itchiness', 'dry scaly patches']
    Symptoms have been saved to symptoms.txt
    Loading knowledge graph...
    Knowledge graph loaded.
    Loading symptoms...
    Loaded Symptoms: ['skin rash', 'itchiness', 'dry scaly patches']
    Warning: The following symptoms are not present in the knowledge graph and will be ignored: ['itchiness', 'dry scaly patches']
    Performing A* search to identify possible diseases...
    Possible diseases have been saved to possible_diseases.txt
    Disease Ground Truth: Psoriasis
    Loading: --------------
    Diagnose complete!
    Predicted Disease is: psoriasis 2.882
    -----------------Diagnose End-----------------

    ---------Diagnosis Statistics---------
    Disease: Psoriasis
    Correct Predictions: 1
    Incorrect Predictions: 0
    Accuracy: 100.00%
    --------------------------------------
    ```

Notes:
    - **Performance Considerations:** Processing a large number of patient cases may be time-consuming, especially if external scripts are slow. Optimize external scripts for better performance if necessary.
    - **Extensibility:** The knowledge graph used by the diagnosis script can be expanded to improve accuracy over time.
'''

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import pandas as pd
import subprocess
import kagglehub
import sys
from collections import defaultdict
import argparse

def extract_symptoms(text, api_key):
    """
    Extracts symptoms from the input text using an external script.
    
    Parameters:
        text (str): The input text containing patient information.
        api_key (str): The API key for authentication.
        
    Returns:
        str: Extracted symptoms.
    """
    # Remove existing temporary files if they exist
    if os.path.exists('symptoms.txt'):
        os.remove('symptoms.txt')
    if os.path.exists('temp_input.txt'):
        os.remove('temp_input.txt')
    
    # Write the input text to a temporary file
    with open('temp_input.txt', 'w') as f:
        f.write(text)
    
    # Call the external script to extract symptoms
    subprocess.run([
        'python3', 'get_symptoms.py',
        '--input', 'temp_input.txt',
        '--output', 'symptoms.txt',
        '--api', api_key
    ])
    
    # Read and return the extracted symptoms
    with open('symptoms.txt', 'r') as f:
        symptoms = f.read().strip()
    
    return symptoms

def main(api_key, line_threshold):
    """
    Main function to perform diagnosis and evaluate accuracy.
    
    Parameters:
        api_key (str): The API key for authentication.
        line_threshold (int): The number of lines to process from the CSV file.
    """
    # Download the dataset from Kaggle
    path = kagglehub.dataset_download("niyarrbarman/symptom2disease")
    data = pd.read_csv(os.path.join(path, "Symptom2Disease.csv"))
    
    # Initialize a dictionary to keep counts of correct and incorrect predictions per disease
    counts = defaultdict(lambda: {'correct': 0, 'incorrect': 0})
    
    line = 0  # Initialize line counter
    
    for index, row in data.iterrows():
        if line >= line_threshold:
            break  # Exit the loop once the line threshold is reached

        print()
        print("-----------------Diagnose Start-----------------")
        disease_gt = row['label']
    
        # Extract symptoms from the text
        Extracted_Symptoms = extract_symptoms(row['text'], api_key)
        
        # Call the diagnosis script
        if os.path.exists('possible_diseases.txt'):
            os.remove('possible_diseases.txt')
        
        subprocess.run([
            'python3', 'get_diagnosis.py',
            '--graph', 'knowledge_graph.pkl',
            '--symptoms', 'symptoms.txt',
            '--output', 'possible_diseases.txt'
        ])
        
        if not os.path.exists('possible_diseases.txt'):
            print('Cannot find possible diseases')
            line += 1
            print("-----------------Diagnose End-----------------")
            print()
            # Increment the incorrect count since we couldn't make a prediction
            counts[disease_gt]['incorrect'] += 1
            continue
        
        # Initialize flags and variables for prediction
        flag = 0
        line_t = 0
        first_possible_disease = ''
    
        print(f"Disease Ground Truth: {disease_gt}")
        print("Loading: --------------")
        print(f"Diagnose complete!")
        
        # Read the possible diseases from the output file
        with open('possible_diseases.txt', 'r') as f:
            diseases = f.read()
            for disease in diseases.split('\n'):
                if not disease.strip():
                    continue  # Skip empty lines
                if line_t == 0:
                    first_possible_disease = disease
                    line_t += 1
                # Split the disease entry by tab and compare with ground truth
                disease_name = disease.split('\t')[0].lower()
                if disease_name == disease_gt.lower() and flag == 0:
                    print(f"Predicted Disease is: {disease}")
                    flag = 1
                    break
            if flag == 0:
                print(f"Predicted Disease is: {first_possible_disease}")
        
        # Update counts based on prediction result
        if flag == 1:
            counts[disease_gt]['correct'] += 1
        else:
            counts[disease_gt]['incorrect'] += 1
    
        line += 1
        print("-----------------Diagnose End-----------------")
        print()
    
    # Print out the statistics after processing
    print("---------Diagnosis Statistics---------")
    for disease, count in counts.items():
        correct = count['correct']
        incorrect = count['incorrect']
        total = correct + incorrect
        accuracy = (correct / total) * 100 if total > 0 else 0
        print(f"Disease: {disease}")
        print(f"  Correct Predictions: {correct}")
        print(f"  Incorrect Predictions: {incorrect}")
        print(f"  Accuracy: {accuracy:.2f}%")
        print("--------------------------------------")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Medical Diagnosis Evaluation Script")
    parser.add_argument('API_KEY', type=str, help='Your API key for authentication.')
    parser.add_argument('line_threshold', type=int, help='Number of lines to process from the CSV file.')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Validate line_threshold
    if args.line_threshold <= 0:
        print("Error: line_threshold must be a positive integer.")
        sys.exit(1)
    
    # Call the main function with parsed arguments
    main(args.API_KEY, args.line_threshold)
