import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def find_max_clique(adj_matrix):
    """
    Extracts the maximum clique from the given adjacency matrix
    
    Parameters:
    adj_matrix: adjacency matrix of the graph (2D list of 0s and 1s)
    
    Returns:
    list representing the vertices that form the largest clique
    """
    n = len(adj_matrix)
    
    # Base case: if the graph is empty
    if n == 0:
        return []
    
    # Initialize the best solution found so far
    max_clique = []
    
    def is_clique(vertices):
        """Check if the given set of vertices forms a clique"""
        for i in vertices:
            for j in vertices:
                if i != j and adj_matrix[i][j] == 0:
                    return False
        return True
    
    def backtrack(candidates, current_clique):
        """Backtracking algorithm to explore all possible cliques"""
        nonlocal max_clique
        
        # If there are no more candidates, check if the current clique is larger
        if not candidates:
            if len(current_clique) > len(max_clique):
                max_clique = current_clique.copy()
            return
        
        # Pruning: can't get a larger clique
        if len(current_clique) + len(candidates) <= len(max_clique):
            return
        
        v = candidates[0]
        new_candidates = []
        
        # Select candidates that can be added to the current clique
        for u in candidates[1:]:
            if adj_matrix[v][u] == 1:
                new_candidates.append(u)
        
        # Include vertex v in the clique
        backtrack(new_candidates, current_clique + [v])
        
        # Exclude vertex v from the clique
        backtrack(candidates[1:], current_clique)
    
    # Start the backtracking search with all vertices as candidates
    backtrack(list(range(n)), [])
    
    return max_clique


class MaxCliqueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maximum Clique Finder")
        self.root.geometry("1000x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left frame for input
        left_frame = ttk.Frame(main_frame, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create right frame for graph visualization
        self.right_frame = ttk.Frame(main_frame, padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Input section
        ttk.Label(left_frame, text="Number of vertices:").pack(anchor=tk.W, pady=(0, 5))
        
        size_frame = ttk.Frame(left_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.size_var = tk.StringVar(value="5")
        size_entry = ttk.Entry(size_frame, textvariable=self.size_var, width=10)
        size_entry.pack(side=tk.LEFT)
        
        ttk.Button(size_frame, text="Create Matrix", command=self.create_matrix).pack(side=tk.LEFT, padx=(10, 0))
        
        # Matrix input section
        self.matrix_frame = ttk.LabelFrame(left_frame, text="Adjacency Matrix", padding="10")
        self.matrix_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.matrix_entries = []
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Find Maximum Clique", command=self.find_clique).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_matrix).pack(side=tk.LEFT)
        
        # Example button
        ttk.Button(left_frame, text="Load Example", command=self.load_example).pack(anchor=tk.W)
        
        # Results section
        self.results_frame = ttk.LabelFrame(left_frame, text="Results", padding="10")
        self.results_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.result_var = tk.StringVar()
        ttk.Label(self.results_frame, textvariable=self.result_var, wraplength=400).pack(fill=tk.X)
        
        # Create initial matrix
        self.create_matrix()
    
    def create_matrix(self):
        # Clear existing entries
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        
        # Get matrix size
        try:
            n = int(self.size_var.get())
            if n <= 0:
                raise ValueError("Size must be positive")
            if n > 15:  # Limit size for usability
                messagebox.showwarning("Warning", "Large matrices may cause performance issues. Limited to 15.")
                n = 15
                self.size_var.set(str(n))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive integer")
            return
        
        # Create matrix entries
        self.matrix_entries = []
        main_frame = ttk.Frame(self.matrix_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create labels for columns
        ttk.Label(main_frame, text=" ").grid(row=0, column=0)
        for i in range(n):
            ttk.Label(main_frame, text=str(i)).grid(row=0, column=i+1, padx=5)
        
        # Create entries for matrix
        for i in range(n):
            row_entries = []
            ttk.Label(main_frame, text=str(i)).grid(row=i+1, column=0, padx=5)
            for j in range(n):
                var = tk.StringVar(value="0")
                entry = ttk.Entry(main_frame, textvariable=var, width=3)
                entry.grid(row=i+1, column=j+1, padx=2, pady=2)
                
                # Disable diagonal entries (self-loops)
                if i == j:
                    entry.config(state="disabled")
                    var.set("0")
                
                # Make entries symmetric
                entry.bind("<FocusOut>", lambda event, i=i, j=j: self.update_symmetric(i, j))
                
                row_entries.append(var)
            self.matrix_entries.append(row_entries)
    
    def update_symmetric(self, i, j):
        if i != j:  # Skip diagonal entries
            value = self.matrix_entries[i][j].get()
            if value not in ["0", "1"]:
                self.matrix_entries[i][j].set("0")
                value = "0"
            self.matrix_entries[j][i].set(value)
    
    def get_matrix(self):
        n = len(self.matrix_entries)
        matrix = []
        
        for i in range(n):
            row = []
            for j in range(n):
                try:
                    val = int(self.matrix_entries[i][j].get())
                    if val not in [0, 1]:
                        raise ValueError
                    row.append(val)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid entry at position ({i}, {j}). Must be 0 or 1.")
                    return None
            matrix.append(row)
        
        return matrix
    
    def find_clique(self):
        matrix = self.get_matrix()
        if matrix is None:
            return
        
        max_clique = find_max_clique(matrix)
        
        # Display results
        if not max_clique:
            self.result_var.set("No clique found.")
        else:
            self.result_var.set(f"Maximum Clique: {max_clique}\nSize: {len(max_clique)}")
        
        # Visualize the graph
        self.visualize_graph(matrix, max_clique)
    
    def visualize_graph(self, matrix, max_clique):
        # Clear previous visualization
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        
        # Create graph
        G = nx.Graph()
        n = len(matrix)
        
        # Add nodes
        for i in range(n):
            G.add_node(i)
        
        # Add edges
        for i in range(n):
            for j in range(i+1, n):
                if matrix[i][j] == 1:
                    G.add_edge(i, j)
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(5, 4))
        
        # Node colors
        node_colors = ['red' if node in max_clique else 'lightblue' for node in G.nodes()]
        
        # Draw graph
        pos = nx.spring_layout(G, seed=42)
        nx.draw(G, pos, with_labels=True, node_color=node_colors, 
                node_size=500, font_size=10, font_weight='bold', ax=ax)
        
        # Highlight clique edges
        clique_edges = [(u, v) for u in max_clique for v in max_clique if u < v and matrix[u][v] == 1]
        nx.draw_networkx_edges(G, pos, edgelist=clique_edges, width=2, edge_color='red', ax=ax)
        
        # Add title
        ax.set_title(f"Graph with Maximum Clique (size {len(max_clique)})")
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.right_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def clear_matrix(self):
        for i in range(len(self.matrix_entries)):
            for j in range(len(self.matrix_entries[i])):
                if i != j:  # Skip diagonal entries
                    self.matrix_entries[i][j].set("0")
    
    def load_example(self):
        # Example adjacency matrix
        example = [
            [0, 1, 1, 1, 1],
            [1, 0, 1, 1, 1],
            [1, 1, 0, 1, 0],
            [1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0]
        ]
        
        # Update size and create matrix
        self.size_var.set(str(len(example)))
        self.create_matrix()
        
        # Fill in the matrix
        for i in range(len(example)):
            for j in range(len(example[i])):
                if i != j:  # Skip diagonal entries
                    self.matrix_entries[i][j].set(str(example[i][j]))


if __name__ == "__main__":
    root = tk.Tk()
    app = MaxCliqueApp(root)
    root.mainloop()