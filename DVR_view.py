import tkinter as tk
from tkinter import messagebox
import DVR_logic

class VisualObject:
    """
    Represents a visual object on the canvas, such as a node or an edge.
    VisualObject instances are used in dictionaries, assosiating the object's identifier with its representation.
    
    Attributes:
        shape (int): The shape identifier on the canvas.
        text (int): The text identifier on the canvas.
        x (float): The x-coordinate of the object on the canvas.
        y (float): The y-coordinate of the object on the canvas.
    """
    def __init__(self, shape: int, text: int, x: float, y: float):
        """
        Initializes the visual representation of an object.
        
        Args:
            shape (int): The shape identifier on the canvas.
            text (int): The text identifier on the canvas.
            x (float): The x-coordinate on the canvas.
            y (float): The y-coordinate on the canvas.
        """
        self.shape: int = shape
        self.text: int = text
        self.x: float = x
        self.y: float = y

class GraphGUI:
    """
    A graphical user interface for managing and simulating a network graph.
    
    Attributes:
        root (tk.Tk): The root Tkinter window.
        idCounter (int): Counter for node IDs.
        NodeList (list): List of WebNode objects in the network.
        NetManager (EdgesMap): Manages edges and nodes in the network.
        nodeVisuals (dict[int, VisualObject]): Stores visual representations of nodes.
        edgeVisuals (dict[tuple[int, int], VisualObject]): Stores visual representations of edges.
    """
    def __init__(self, root):
        """
        Initializes the Graph GUI and sets up the Tkinter widgets and canvas.
        
        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("DVR Simulator")
        
        # Initialize attributes
        self.idCounter = 1
        self.NodeList:list[DVR_logic.WebNode] = []
        self.NetManager:DVR_logic.EdgesMap = DVR_logic.EdgesMap()
        self.nodeVisuals:dict[int, VisualObject] = {}
        self.edgeVisuals:dict[tuple[int, int], VisualObject] = {}
        
        # Set up the canvas for graphical display
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind("<Button-1>", self.createNode)
        self.canvas.bind("<Button-3>", self.handleRightClick)
        
        # Set up control frame for inputs and buttons
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(control_frame, text="Source").pack()
        self.src_entry = tk.Entry(control_frame)
        self.src_entry.pack()
        
        tk.Label(control_frame, text="Destination").pack()
        self.dst_entry = tk.Entry(control_frame)
        self.dst_entry.pack()
        
        tk.Label(control_frame, text="Weight").pack()
        self.w_entry = tk.Entry(control_frame)
        self.w_entry.pack()
        
        add_edge_button = tk.Button(control_frame, text="Add Edge", command=self.addEdge)
        add_edge_button.pack(pady=5)
        
        execute_button = tk.Button(control_frame, text="Print routing tables", command=self.printRoutingTables)
        execute_button.pack(side='bottom', pady=5)

    def createNode(self, event):
        """
        Creates a new node at the location of a left mouse click.
        
        Args:
            event (tk.Event): The mouse event containing the click location.
        """
        newNode = self.NetManager.addNode(self.idCounter)
        if newNode != None:
            self.NodeList.append(newNode)
            
            x, y = event.x, event.y
            shape = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="blue")
            text = self.canvas.create_text(x, y, text=str(self.idCounter), fill="white")
            
            self.nodeVisuals[self.idCounter] = VisualObject(shape, text, x, y)
            self.idCounter += 1

    def addEdge(self):
        """
        Adds an edge between two nodes using input from the control panel.
        Validates input and ensures edge does not already exist.
        """
        try:
            if not self.src_entry.get().isdigit():
                raise ValueError("Source must be an integer")
            if not self.dst_entry.get().isdigit():
                raise ValueError("Destination must be an integer")
            if not self.w_entry.get().isdigit():
                raise ValueError("Weight must be an integer")
            
            src = int(self.src_entry.get())
            dst = int(self.dst_entry.get())
            w = int(self.w_entry.get())
            
            self.src_entry.delete(0, tk.END)
            self.dst_entry.delete(0, tk.END)
            self.w_entry.delete(0, tk.END)

            
            if src == dst or DVR_logic.findNodePos(src, self.NodeList) == None or DVR_logic.findNodePos(dst, self.NodeList) == None:
                raise ValueError("Invalid nodes")
        
            if w <= 0:
                raise ValueError("Invalid weight")
            
            if (min(src, dst), max(src, dst)) in self.edgeVisuals.keys():
                raise ValueError("The edge already exists")
            
            x1, y1 = self.nodeVisuals[src].x, self.nodeVisuals[src].y
            x2, y2 = self.nodeVisuals[dst].x, self.nodeVisuals[dst].y
            
            shape = self.canvas.create_line(x1, y1, x2, y2, fill="black")
            self.canvas.tag_lower(shape)
            x, y = (x1 + x2) / 2, (y1 + y2) / 2
            text = self.canvas.create_text(x, y, text=str(w), fill="red")
            
            self.edgeVisuals[(min(src, dst), max(src, dst))] = VisualObject(shape, text, x, y)
            self.NetManager.addEdge(src, dst, w, self.NodeList)
            
            DVR_logic.updateNet(self.NodeList, self.NetManager, [src, dst])
            
        except ValueError as ve:
            messagebox.showerror("Error", ve)

    def findClosestItem(self, event) -> tuple[int, int]:
        """
        Finds the closest visual object (node or edge) to the given click location.
        
        Args:
            event (tk.Event): The mouse event containing the click location.
        
        Returns:
            tuple[int, int]: A tuple containing the closest node or edge id.
            - If a node is closer -> (nodeId, None)
            - If an edge is closer -> (srcId, dstId)
            - If no objects are found -> (None, None)
        """
        minDistNode = None
        minDistEdge = None
        minNode = None
        minEdge = None
        
        for k in self.nodeVisuals:
            dist = abs(self.nodeVisuals[k].x - event.x) + abs(self.nodeVisuals[k].y - event.y)
            if minNode == None or minDistNode > dist:
                minNode = k
                minDistNode = dist
        
        for k in self.edgeVisuals:
            dist = abs(self.edgeVisuals[k].x - event.x) + abs(self.edgeVisuals[k].y - event.y)
            if minEdge == None or minDistEdge > dist:
                minEdge = k
                minDistEdge = dist
        
        if minEdge == None or minDistNode < minDistEdge:
            return (minNode, None)
        elif minNode == None or minDistNode > minDistEdge:
            return minEdge
        else:
            return (None, None)
    
    def handleRightClick(self, event):
        """
        Handles a right-click event to delete a node or edge.
        
        Args:
            event (tk.Event): The mouse event containing the click location.
        """
        items = self.findClosestItem(event)
        if items[0] != None:
            if items[1] == None:
                self.deleteNode(items[0])
            else:
                self.deleteEdge(items)

    def deleteNode(self, id: int):
        """
        Deletes a node and all associated edges from the graph and canvas.
        
        Args:
            id (int): The identifier of the node to delete.
        """
        if messagebox.askyesno("Confirm Deletion", f"Do you want to delete node {id}?"):
            
            self.canvas.delete(self.nodeVisuals[id].shape)
            self.canvas.delete(self.nodeVisuals[id].text)
            del self.nodeVisuals[id]
            
            nbs = self.NetManager.getNeighborsId(id)
            
            for e in self.NetManager.getEdges(id):
                edge = (min(id, e.dst), max(id, e.dst))
                if edge in self.edgeVisuals.keys():
                    self.canvas.delete(self.edgeVisuals[edge].shape)
                    self.canvas.delete(self.edgeVisuals[edge].text)
                    del self.edgeVisuals[edge]
                    
            self.NetManager.removeNode(id, self.NodeList)
            DVR_logic.updateNet(self.NodeList, self.NetManager, nbs)

    def deleteEdge(self, edgeIds:tuple[int, int]):
        """
        Deletes an edge from the graph and canvas.
        
        Args:
            edgeIds (tuple[int, int]): The identifiers of the two nodes connected by the edge.
        """
        edge = (min(edgeIds[0], edgeIds[1]), max(edgeIds[0], edgeIds[1]))
        
        if edge in self.edgeVisuals.keys():
            if messagebox.askyesno("Confirm Deletion", f"Do you want to delete edge {edge[0]} - {edge[1]}?"):
                self.canvas.delete(self.edgeVisuals[edge].shape)
                self.canvas.delete(self.edgeVisuals[edge].text)
                del self.edgeVisuals[edge]
                self.NetManager.removeEdge(edge[0], edge[1], self.NodeList)
                DVR_logic.updateNet(self.NodeList, self.NetManager, [edge[0], edge[1]])

    def printRoutingTables(self):
        """
        Writes the routing tables of all nodes to a file and displays a success message.
        """
        path = 'RoutingTables.txt'
        
        with open(path, 'w') as file:
            for wn in self.NodeList:
                file.write(str(wn)+"\n")
                # for e in wn.getRoutingMap().keys():
                #     if not DVR_logic.is_minimum_distance(self.NetManager.getMap(), wn.getId(), e, wn.getRoutingMap()[e].dist):
                #         file.write(f"{wn.getId()} -> {e} is wrong\n\n")
                                    
            file.write(str(self.NetManager)+"\n")
                
        messagebox.showinfo("Routing Tables", f"The routing tables were successfully printed in {path}")

def main():
    with open('log.txt', "w"):
        pass
    root = tk.Tk()
    app = GraphGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()