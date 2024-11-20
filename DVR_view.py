import tkinter as tk
from tkinter import messagebox
import DVR_logic

class VisualObject:
    def __init__(self, shape:int, text:int, x:float, y:float):
        self.shape:int = shape
        self.text:int = text
        self.x:float = x
        self.y:float = y

class GraphGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DVR Simulator")
        
        self.idCounter = 1
        self.NodeList:list[DVR_logic.WebNode] = []
        self.NetManager:DVR_logic.EdgesMap = DVR_logic.EdgesMap()
        self.nodeVisuals:dict[int, VisualObject] = {}
        self.edgeVisuals:dict[tuple[int, int], VisualObject] = {}
        
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind("<Button-1>", self.createNode)
        self.canvas.bind("<Button-3>", self.handleRightClick)
        
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(control_frame, text="Source").pack()
        self.source_entry = tk.Entry(control_frame)
        self.source_entry.pack()
        
        tk.Label(control_frame, text="Destination").pack()
        self.dest_entry = tk.Entry(control_frame)
        self.dest_entry.pack()
        
        tk.Label(control_frame, text="Weight").pack()
        self.weight_entry = tk.Entry(control_frame)
        self.weight_entry.pack()
        
        add_edge_button = tk.Button(control_frame, text="Add Edge", command=self.addEdge)
        add_edge_button.pack(pady=5)
        
        execute_button = tk.Button(control_frame, text="Print routing tables", command=self.printRoutingTables)
        execute_button.pack(side='bottom', pady=5)

    def createNode(self, event):
        newNode = self.NetManager.addNode(self.idCounter)
        if newNode != None:
            self.NodeList.append(newNode)
            
            x, y = event.x, event.y
            shape = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="blue")
            text = self.canvas.create_text(x, y, text=str(self.idCounter), fill="white")
            
            self.nodeVisuals[self.idCounter] = VisualObject(shape, text, x, y)
            self.idCounter += 1

    def addEdge(self):
        try:
            if not self.source_entry.get().isdigit():
                raise ValueError("Source must be an integer")
            if not self.dest_entry.get().isdigit():
                raise ValueError("Destination must be an integer")
            if not self.weight_entry.get().isdigit():
                raise ValueError("Weight must be an integer")
            
            src = int(self.source_entry.get())
            dst = int(self.dest_entry.get())
            w = int(self.weight_entry.get())
            
            self.source_entry.delete(0, tk.END)
            self.dest_entry.delete(0, tk.END)
            self.weight_entry.delete(0, tk.END)

            
            if src == dst or DVR_logic.findNodePos(src, self.NodeList) == None or DVR_logic.findNodePos(dst, self.NodeList) == None:
                raise ValueError("Invalid nodes")
        
            if w <= 0:
                raise ValueError("Invalid weight")
            
            if (min(src, dst), max(src, dst)) in self.edgeVisuals.keys():
                raise ValueError("The edge already exists")
            
            x1, y1 = self.nodeVisuals[src].x, self.nodeVisuals[src].y
            x2, y2 = self.nodeVisuals[dst].x, self.nodeVisuals[dst].y
            
            shape = self.canvas.create_line(x1, y1, x2, y2)
            self.canvas.tag_lower(shape)
            x, y = (x1 + x2) / 2, (y1 + y2) / 2
            text = self.canvas.create_text(x, y, text=str(w), fill="red")
            
            self.edgeVisuals[(min(src, dst), max(src, dst))] = VisualObject(shape, text, x, y)
            self.NetManager.addEdge(src, dst, w, self.NodeList)
            
            DVR_logic.updateNet(self.NodeList, self.NetManager)
            
        except ValueError as ve:
            messagebox.showerror("Error", ve)

    def findClosestItem(self, event) -> tuple[int, int]:
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
        items = self.findClosestItem(event)
        if items[0] != None:
            if items[1] == None:
                self.deleteNode(items[0])
            else:
                self.deleteEdge(items)

    def deleteNode(self, id: int):
        
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
        edge = (min(edgeIds[0], edgeIds[1]), max(edgeIds[0], edgeIds[1]))
        
        if edge in self.edgeVisuals.keys():
            if messagebox.askyesno("Confirm Deletion", f"Do you want to delete edge {edge[0]} - {edge[1]}?"):
                self.canvas.delete(self.edgeVisuals[edge].shape)
                self.canvas.delete(self.edgeVisuals[edge].text)
                del self.edgeVisuals[edge]
                self.NetManager.removeEdge(edge[0], edge[1], self.NodeList)
                DVR_logic.updateNet(self.NodeList, self.NetManager, [edge[0], edge[1]])

    def printRoutingTables(self):
        
        path = 'RoutingTables.txt'
        
        with open(path, 'w') as file:
            for wn in self.NodeList:
                file.write(str(wn)+"\n")
            file.write(str(self.NetManager)+"\n")
                
        messagebox.showinfo("Routing Tables", f"The routing tables were successfully printed in {path}")

def main():
    root = tk.Tk()
    app = GraphGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()