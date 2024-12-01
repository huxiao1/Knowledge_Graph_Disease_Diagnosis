'''
Topic:
    Identify possible diseases using A* algorithm based on the knowledge graph and extracted symptoms.

Usage:
    --graph: Path to the input knowledge graph pickle file (required).
    --symptoms: Path to the input symptoms file (required).
    --output: Path to the output possible diseases file, default is possible_diseases.txt.

    Example:
        `python3 get_diagnosis.py --graph knowledge_graph.pkl --symptoms symptoms.txt`
        `python3 get_diagnosis.py --graph knowledge_graph.pkl --symptoms symptoms.txt --output possible_diseases.txt`

Input Format:
    symptoms.txt
    severe abdominal pain
    nausea
    vomiting
    occasional heartburn
    difficulty swallowing

Output Format:
    possible_diseases.txt
    acid reflux    2.041
    abscess    3.156
    ...
    
    Also prints the list of possible diseases with their scores to the console.

Notes:
    - The A* algorithm uses the negative logarithm of association strengths as costs.
    - The heuristic function estimates the minimal remaining cost to reach any disease.
    - Diseases with lower cumulative costs are ranked higher (more likely).
'''

import os
# set the number of threads to 1 for better performance cuz purdue server sucks!
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import argparse
import pickle
import networkx as nx
from math import log
from heapq import heappush, heappop

def load_graph(graph_path):
    with open(graph_path, 'rb') as f:
        G = pickle.load(f)
    return G

def load_symptoms(symptoms_path):
    with open(symptoms_path, 'r', encoding='utf-8') as f:
        symptoms = [line.strip().lower() for line in f if line.strip()]
    return symptoms

def heuristic(node, G):
    """
    Heuristic function: estimate the minimal remaining cost to reach any disease from the current node.
    We use the minimum negative log(weight) among all connected edges.
    """
    if G.nodes[node].get('group') == 'disease':
        return 0
    # Find the minimum negative log(weight) of edges connected to this node
    weights = [edge_weight(G, node, neighbor) for neighbor in G.neighbors(node)]
    if not weights:
        return 0  # No connected edges, heuristic is zero
    min_cost = min(weights)
    return min_cost

def edge_weight(G, u, v):
    """
    Calculate the cost to traverse an edge using negative logarithm of the weight.
    """
    weight = G[u][v].get('weight', 0.0)
    if weight <= 0:
        return float('inf')  # Assign infinite cost for zero or negative weights
    return -log(weight)

def a_star_search(G, symptoms):
    """
    Perform A* search from the symptoms to all possible diseases.
    Returns a list of diseases sorted by their cumulative costs in ascending order.
    """
    # Initialize priority queue
    queue = []
    # Initialize costs dictionary
    costs = {}
    # Initialize visited set
    visited = set()
    
    # Initialize the queue with all symptoms as starting points
    for symptom in symptoms:
        heappush(queue, (heuristic(symptom, G), symptom, 0))
        costs[symptom] = 0
    
    while queue:
        estimated_total_cost, current_node, current_cost = heappop(queue)
        
        if current_node in visited:
            continue
        visited.add(current_node)
        
        # If the current node is a disease, record its cumulative cost
        if G.nodes[current_node].get('group') == 'disease':
            costs[current_node] = current_cost
            continue
        
        # Explore neighbors
        for neighbor in G.neighbors(current_node):
            if neighbor in visited:
                continue
            cost = edge_weight(G, current_node, neighbor)
            if cost == float('inf'):
                continue
            neighbor_cost = current_cost + cost
            # If this path to neighbor is better, record it
            if neighbor not in costs or neighbor_cost < costs[neighbor]:
                costs[neighbor] = neighbor_cost
                estimated_cost = neighbor_cost + heuristic(neighbor, G)
                heappush(queue, (estimated_cost, neighbor, neighbor_cost))
    
    # Extract diseases and their cumulative costs
    disease_scores = {}
    for node, data in G.nodes(data=True):
        if data.get('group') == 'disease' and node in costs:
            disease_scores[node] = costs[node]
    
    # Sort diseases by cumulative cost in ascending order (lower cost means higher likelihood)
    sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1])
    
    return sorted_diseases

def save_possible_diseases(diseases, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for disease, score in diseases:
                f.write(f"{disease}\t{score:.3f}\n")
        print(f"Possible diseases have been saved to {output_path}")
    except Exception as e:
        print(f"Error writing to file {output_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Stage 3: Identify possible diseases using A* algorithm.")
    parser.add_argument('--graph', required=True, type=str, help='Path to the input knowledge graph pickle file')
    parser.add_argument('--symptoms', required=True, type=str, help='Path to the input symptoms file')
    parser.add_argument('--output', type=str, default='possible_diseases.txt', help='Path to the output possible diseases file')
    
    args = parser.parse_args()
    
    # Load the knowledge graph
    print("Loading knowledge graph...")
    G = load_graph(args.graph)
    print("Knowledge graph loaded.")
    
    # Load the symptoms
    print("Loading symptoms...")
    symptoms = load_symptoms(args.symptoms)
    print(f"Loaded Symptoms: {symptoms}")
    
    # Check if symptoms exist in the graph
    missing_symptoms = [s for s in symptoms if s not in G.nodes()]
    if missing_symptoms:
        print(f"Warning: The following symptoms are not present in the knowledge graph and will be ignored: {missing_symptoms}")
        symptoms = [s for s in symptoms if s in G.nodes()]
    
    if not symptoms:
        print("Error: No valid symptoms found in the knowledge graph.")
        return
    
    # Perform A* search to identify possible diseases
    print("Performing A* search to identify possible diseases...")
    sorted_diseases = a_star_search(G, symptoms)
    
    if not sorted_diseases:
        print("No diseases identified based on the provided symptoms.")
        return
    
    # Save the possible diseases to a file
    save_possible_diseases(sorted_diseases, args.output)
    
    # Print the possible diseases
    print("\nPossible Diseases:")
    for disease, score in sorted_diseases:
        print(f"Disease: {disease.title()}, Score (lower is better): {score:.3f}")

if __name__ == "__main__":
    main()
