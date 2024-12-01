## Overview

This project identifies potential diseases based on patient symptoms using AI and graph-based methods:

1. Knowledge Graph: Build a graph linking diseases and symptoms with weighted associations.
2. Symptom Extraction: Use ChatGPT to extract symptoms from patient descriptions.
3. Disease Search: Apply the A* algorithm to find the most likely diseases.
4. Diagnosis Output: Provide doctors with a ranked list of potential diseases.

---

## Installation

1. Install dependencies using the provided `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

2. Verify that the required packages are installed:
    ```bash
    pip list
    ```

---

### 1. Build a Knowledge Graph
#### **Description**
Generates a knowledge graph from a CSV file of diseases and their associated symptoms.

#### **Usage**
```bash
python3 get_knowledge_graph.py --csv DerivedKnowledgeGraph_final.csv
```

Options:
- **Static Visualization:**
    ```bash
    python3 get_knowledge_graph.py --csv DerivedKnowledgeGraph_final.csv --visualization static --output_image knowledge_graph.png
    ```
- **Interactive Visualization:**
    ```bash
    python3 get_knowledge_graph.py --csv DerivedKnowledgeGraph_final.csv --visualization interactive --output_html knowledge_graph.html
    ```

#### **Input Format**
CSV File:
```plaintext
Diseases | Symptoms
abscess  | pain (0.318), fever (0.119), swelling (0.112), redness (0.094), chills (0.092), ...
...      | ...
```

#### **Output Format**
- **Pickle File:** `knowledge_graph.pkl`
- **Static Image:** `knowledge_graph.png`
- **Interactive HTML:** `knowledge_graph.html`

---

### 2. Extract Patient Symptoms
#### **Description**
Extract symptoms from a patient's description using ChatGPT or manual input.

#### **Usage**
There are two options for extracting symptoms:
1. **Using ChatGPT:**
    ```bash
    python3 get_symptoms.py --input patient_description.txt --output symptoms.txt --api YOUR_API_KEY
    ```
2. **Manual Input:**
    ```bash
    python3 get_symptoms.py --output symptoms.txt
    ```

    Prompt We Used to Get the Patient Description:
    ```
    You are an experienced medical assistant. Based on the patient's description provided below, extract the key symptoms that the patient is experiencing. Please list the symptoms as a comma-separated list in English.

    Patient Description:
    The patient is experiencing severe abdominal pain, nausea, and vomiting. 
    They also report occasional heartburn and difficulty swallowing.

    Extracted Symptoms:
    ```

#### **Input Format**
- **With ChatGPT:**
    ```plaintext
    The patient is experiencing severe abdominal pain, nausea, and vomiting. 
    They also report occasional heartburn and difficulty swallowing.
    ```
- **Manual Input:**
    ```plaintext
    severe abdominal pain, nausea, vomiting, occasional heartburn, difficulty swallowing
    ```

#### **Output Format**
Symptoms are saved to `symptoms.txt`:
```plaintext
severe abdominal pain
nausea
vomiting
occasional heartburn
difficulty swallowing
```

---

### 3. Identify Possible Diseases
#### **Description**
Identifies possible diseases based on extracted symptoms and a pre-built knowledge graph using the A* algorithm.

#### **Usage**
```bash
python3 get_diagnosis.py --graph knowledge_graph.pkl --symptoms symptoms.txt
```

Options:
- Specify an output file for possible diseases:
    ```bash
    python3 get_diagnosis.py --graph knowledge_graph.pkl --symptoms symptoms.txt --output possible_diseases.txt
    ```

#### **Input Format**
- **Symptoms File (`symptoms.txt`):**
    ```plaintext
    severe abdominal pain
    nausea
    vomiting
    occasional heartburn
    difficulty swallowing
    ```

#### **Output Format**
- **Diseases File (`possible_diseases.txt`):**
    ```plaintext
    stomach flu	0.642
    gastroparesis	0.662
    appendicitis	0.914
    pancreatitis	1.115
    ...
    ```

The list of diseases with their scores is also printed to the console.

#### **Notes**
- The A* algorithm uses the negative logarithm of association strengths as costs.
- Diseases with lower cumulative costs are ranked higher (more likely).

---

## References
[HealthKnowledgeGraph](https://github.com/clinicalml/HealthKnowledgeGraph/tree/master) 


## Notes

- Ensure the API key for ChatGPT is valid when extracting symptoms automatically.
- The CSV file for the knowledge graph must include diseases and symptoms in the expected format.
- Generated knowledge graphs can be visualized in both static (PNG) and interactive (HTML) formats.