import copy
import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Define global variables
canvas = None

def distance_vector_routing(graph):

    nodes = list(graph.keys())
    iterations = 0
    routing_tables_history = []

    # Initialize routing tables with hop count as cost metric
    routing_tables = {node: {other_node: float('inf') for other_node in nodes} for node in nodes}
    for node, neighbors in graph.items():
        for neighbor, cost in neighbors.items():
            routing_tables[node][neighbor] = cost

    # Loop until convergence (no changes in routing tables)
    while True:
        iterations += 1
        changed = False

        # Update routing tables for each node
        for node in nodes:
            new_routing_table = copy.deepcopy(routing_tables[node])
            for neighbor, cost in graph[node].items():
                for destination_node in nodes:
                    # Bellman-Ford equation to find shortest path
                    new_cost = cost + routing_tables[neighbor][destination_node]
                    if new_cost < new_routing_table[destination_node]:
                        new_routing_table[destination_node] = new_cost

            # Check for changes and update tables
            if new_routing_table != routing_tables[node]:
                changed = True
                routing_tables[node] = new_routing_table

        # Append current routing tables to history
        routing_tables_history.append(copy.deepcopy(routing_tables))

        # Stop if no changes in any table
        if not changed:
            break

    return routing_tables, iterations, routing_tables_history

def print_updated_graph_window(graph, routing_table, source, destination):
   

    # Create a new window
    graph_window = tk.Toplevel()
    graph_window.title("Updated Graph")

    # Create canvas for displaying graph
    fig, ax = plt.subplots()
    G = nx.Graph()
    for node, neighbors in graph.items():
        for neighbor, cost in neighbors.items():
            G.add_edge(node, neighbor, weight=cost)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, ax=ax)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    nx.draw_networkx_nodes(G, pos, nodelist=[source], node_color='b', node_size=700)
    nx.draw_networkx_nodes(G, pos, nodelist=[destination], node_color='r', node_size=700)
    shortest_path = nx.shortest_path(nx.Graph(graph), source=source, target=destination, weight='weight')
    edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='g', width=3)
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def calculate_routing_with_default_graph():
    source = source_node_entry.get()
    destination = destination_node_entry.get()

    if not source or not destination:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Please provide both source and destination nodes.")
        return

    graph = get_default_graph()
    
    # Initialize routing tables with direct connections
    routing_tables = {node: {other_node: float('inf') for other_node in graph} for node in graph}
    for node, neighbors in graph.items():
        for neighbor, cost in neighbors.items():
            routing_tables[node][neighbor] = cost

    # Display initial routing tables for iteration 0
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Iteration 0:\n")
    for node, table in routing_tables.items():
        result_text.insert(tk.END, f"Node {node}: {table}\n")
    result_text.insert(tk.END, "\n")

    # Run distance vector routing algorithm
    routing_tables, iterations, routing_tables_history = distance_vector_routing(graph)

    # Display results in the GUI
    result_text.insert(tk.END, f"Number of iterations taken to complete the graph: {iterations}\n\n")
    for i, routing_table in enumerate(routing_tables_history):
        result_text.insert(tk.END, f"Iteration {i + 1}:\n")
        for node, table in routing_table.items():
            result_text.insert(tk.END, f"Node {node}: {table}\n")
        result_text.insert(tk.END, "\n")

    # Calculate shortest paths
    shortest_path_cost = routing_tables_history[-1][source][destination]

    # Display shortest path cost from source to destination
    result_text.insert(tk.END, f"Shortest Path Cost from {source} to {destination}: {shortest_path_cost}\n")

    # Update graph with shortest path in a new window
    print_updated_graph_window(graph, routing_tables, source, destination)




def get_default_graph():
    """
    Define a default network graph.

    Returns:
        dict: The default network graph.
    """
    # Define the default network graph with 6 nodes
    graph = {
        'A': {'B': 2, 'C': 1, 'F': 5},
        'B': {'A': 2, 'C': 2, 'D': 1},
        'C': {'A': 1, 'B': 2, 'D': 4},
        'D': {'B': 1, 'C': 4, 'E': 3},
        'E': {'D': 3, 'F': 2},
        'F': {'A': 5, 'E': 2}
    }
    return graph

# Create main window
root = tk.Tk()
root.title("Distance Vector Routing GUI")

# Create frames
input_frame = ttk.Frame(root)
input_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Source node input
source_node_label = ttk.Label(input_frame, text="Enter the source node:(A-F)")
source_node_label.grid(row=0, column=0, padx=5, pady=5)
source_node_entry = ttk.Entry(input_frame)
source_node_entry.grid(row=0, column=1, padx=5, pady=5)

# Destination node input
destination_node_label = ttk.Label(input_frame, text="Enter the destination node:(A-F)")
destination_node_label.grid(row=1, column=0, padx=5, pady=5)
destination_node_entry = ttk.Entry(input_frame)
destination_node_entry.grid(row=1, column=1, padx=5, pady=5)

# Button to calculate routing
calculate_button = ttk.Button(input_frame, text="Calculate Routing", command=calculate_routing_with_default_graph)
calculate_button.grid(row=2, columnspan=2, padx=5, pady=10)

# Text widget to display results
result_text = tk.Text(input_frame, wrap=tk.WORD, height=30, width=110, font=("Helvetica", 12))  # Adjust height and width as needed
result_text.grid(row=5, columnspan=2, padx=5, pady=10, sticky="nsew")

# Scrollbar for text widget
scrollbar = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=result_text.yview)
scrollbar.grid(row=5, column=2, sticky="ns")
result_text.config(yscrollcommand=scrollbar.set)


# Start GUI
root.mainloop()
