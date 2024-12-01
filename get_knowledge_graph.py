'''
Topic:
    Build a knowledge graph from the CSV data.

Usage:
    --csv: Input CSV file path (required).
    --graph_output: Output pickle file path, default is knowledge_graph.pkl.
    --visualization: Visualization type, select static or interactive, default is static.
    --output_image: Output image path for static visualization, default is knowledge_graph.png.
    --output_html: Output HTML file path for interactive visualization, default is knowledge_graph.html.
        Default Example (Static Visualization, and default output file):
        `python3 get_knowledge_graph.py --csv DerivedKnowledgeGraph_final.csv`
        Static Visualization Example:
        `python3 get_knowledge_graph.py --csv DerivedKnowledgeGraph_final.csv --visualization static --output_image knowledge_graph.png`
        Interactive Visualization Example:
        `python3 get_knowledge_graph.py --csv DerivedKnowledgeGraph_final.csv --visualization interactive --output_html knowledge_graph.html`

Input Format:
    `cat DerivedKnowledgeGraph_final.csv`
    Diseases |	Symptoms
    abscess	 |  pain (0.318), fever (0.119), swelling (0.112), redness (0.094), chills (0.092), infection (0.083), cyst (0.047), tenderness (0.037), rectal pain (0.026), lesion (0.025), lump (0.023), sore throat (0.021), facial swelling (0.016), pimple (0.016), discomfort (0.014), difficulty swallowing (0.013), cavity (0.013), night sweats (0.007), severe pain (0.007), abdominal pain (0.007), painful swallowing (0.007), back pain (0.006)
    ...

Output Format:
    just run the script and it will save the knowledge graph to a pickle file and visualize it as a static or interactive graph.
'''

import os
# set the number of threads to 1 for better performance cuz purdue server sucks!
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import argparse
import csv
import networkx as nx
import pickle
from pyvis.network import Network
import matplotlib.pyplot as plt

def build_knowledge_graph(csv_file):
    G = nx.Graph()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        index = 0
        for row in reader:
            disease = row[0].strip().lower()
            symptoms_data = row[1].split(',')
            for symptom_info in symptoms_data:
                symptom, weight = symptom_info.strip().rsplit(' ', 1)
            
                if index == 0:
                    print(symptom_info)
                    print(symptom)
                    print(float(weight.strip('()')))
                
                weight = float(weight.strip('()'))
                G.add_node(disease, title=disease, group='disease', color='red', size=30)
                G.add_node(symptom, title=symptom, group='symptom', color='blue', size=10)
                G.add_edge(disease, symptom, weight=weight)
            index += 1
    return G

def save_graph_to_file(G, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(G, f)

def get_label_position(pos, offset_x=0.0, offset_y=10):
    return {node: (coords[0] + offset_x, coords[1] + offset_y) for node, coords in pos.items()}

def visualize_graph(G, visualization_type, output_image=None, output_html=None):
    if visualization_type == 'static':
        # Use matplotlib to create a static image
        pos = nx.spring_layout(G, scale=200)  # positions for all nodes with more space
        # nodes
        node_sizes = [1 * G.degree[n] for n in G]  # size nodes based on degree
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=[data['color'] for v, data in G.nodes(data=True)])
        # edges
        nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.5)
        # labels
        # 使用偏移函数
        label_pos = get_label_position(pos, offset_x=0, offset_y=6)
        # 绘制标签
        nx.draw_networkx_labels(G, label_pos, font_size=4, font_family='sans-serif')
        
        plt.axis('off')  # turn off the axis
        plt.savefig(output_image, dpi=300)  # higher dpi for better resolution
        plt.close()
        print(f"Static knowledge graph image saved to {output_image}")
    elif visualization_type == 'interactive':
        # Interactive visualization using pyvis
        net = Network(notebook=False)
        for node, data in G.nodes(data=True):
            net.add_node(node, title=node, color=data['color'], size=data['size'])
        for source, target, data in G.edges(data=True):
            net.add_edge(source, target, title=f"Weight: {data['weight']}")
        net.show_buttons(filter_=['physics'])
        net.show(output_html, notebook=False)
        print(f"Interactive knowledge graph HTML saved to {output_html}")

def main():
    parser = argparse.ArgumentParser(description="Build and visualize a knowledge graph from CSV data.")
    parser.add_argument('--csv', required=True, type=str, help='Input CSV file path')
    parser.add_argument('--graph_output', type=str, default='knowledge_graph.pkl', help='Output pickle file path')
    parser.add_argument('--visualization', type=str, default='static', choices=['static', 'interactive'], help='Visualization type')
    parser.add_argument('--output_image', type=str, default='knowledge_graph.png', help='Output image path for static visualization')
    parser.add_argument('--output_html', type=str, default='knowledge_graph.html', help='Output HTML file path for interactive visualization')

    args = parser.parse_args()

    # Build the knowledge graph from the CSV data
    G = build_knowledge_graph(args.csv)

    # Save the graph to a pickle file
    save_graph_to_file(G, args.graph_output)

    # Visualize the graph based on the selected visualization type
    if args.visualization == 'static':
        visualize_graph(G, 'static', output_image=args.output_image)
    elif args.visualization == 'interactive':
        visualize_graph(G, 'interactive', output_html=args.output_html)

    print(f"Knowledge graph has been built and visualized. Data saved to {args.graph_output}.")

if __name__ == "__main__":
    main()
