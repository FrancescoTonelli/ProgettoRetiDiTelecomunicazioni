from tabulate import tabulate

class RoutingMapEntry:
    """
    Represents a single entry in a node's routing table.\n
    The routing table of a node is a dictionary where the keys represent the destination nodes, 
    and the values are instances of RoutingMapEntry.

    Attributes:
        dist (int): The distance to the destination node.
        nextHop (int): The next hop node id to reach the destination.
    """
    def __init__(self, dist:int, nextHop: int):
        """
        Initializes a RoutingMapEntry with distance and next hop.

        Args:
            dist (int): The distance to the destination node.
            nextHop (int): The next hop node id.
        """
        self.dist:int = dist
        self.nextHop:int = nextHop
        
class EdgeMapEntry:
    """
    Represents an edge in an edge map.\n
    In the EdgesMap, the physical edges are stored in a dictionary, 
    where the keys are the nodes present in the network, 
    and the values are lists of EdgeMapEntry instances for each node 

    Attributes:
        dst (int): The destination node id.
        w (int): The weight of the edge.
    """
    def __init__(self, dst:int, w: int):
        """
        Initializes an EdgeMapEntry instance representing an edge.

        Args:
            dst (int): The destination node id.
            w (int): The weight of the edge.
        """
        self.dst:int = dst
        self.w:int = w

class WebNode:
    """
    Represents a node in the network with a unique id and routing capabilities.

    Attributes:
        __routingMap (dict[int, RoutingMapEntry]): The routing table of the node.
        __id (int): The unique identifier of the node.
    """
    
    def __init__(self, id:int):
        """
        Initializes a WebNode with a unique ID and an empty routing table.

        Args:
            id (int): The unique identifier for the node.
        """
        self.__routingMap:dict[int, RoutingMapEntry] = {}
        self.__id:int = id
        
    def getId(self) -> int:
        """
        Returns the unique identifier of the node.

        Returns:
            int: The unique id of the node.
        """
        return self.__id
    
    def getRoutingMap(self) -> dict[int, RoutingMapEntry]:
        """
        Returns the routing map of the node.

        Returns:
            dict[int, RoutingMapEntry]: The node's routing table.
        """
        return self.__routingMap
    
    def __str__(self):
        """
        Returns a string representation of the node's routing table in tabular format.

        Returns:
            str: The routing table formatted as a table.
        """
        if len(self.__routingMap.keys()) > 0:
            table_data = [
                [str(k), str(self.__routingMap[k].dist), str(self.__routingMap[k].nextHop)]
                for k in self.__routingMap.keys()
            ]
        else:
            table_data = [
                [" ", " ", " "]
            ]

        table = tabulate(
            table_data,
            headers=["Destination", "Distance", "Next Hop"],
            tablefmt="simple",
            colalign=("left", "left", "left")
        )

        return f"Node {str(self.__id)}'s routing table:\n{table}\n"

    def updateRoutes(self, senderId: int, routingMap: dict[int, RoutingMapEntry]) -> bool:
        """
        Updates the node's routing table based on information from a neighboring node.
        - If the sender is not registered, the node adds it to its routing table.
        - If the node still cannot register the sender, it stops and returns False.
        - If any of the node's routes passing through the sender are no longer reachable, it removes them.
        - The node updates its routing table with the sender's table if the sender's routes are better than the current ones or if they do not already exist.
            
        Args:
            senderId (int): The id of the sender node providing the routing update.
            routingMap (dict[int, RoutingMapEntry]): The routing table of the sender node.

        Returns:
            bool: True if the routing table was updated, False otherwise.
        """
        registeredSender = senderId in self.__routingMap.keys()
        
        if self.__id in routingMap.keys() and (not registeredSender or self.__routingMap[senderId].dist > routingMap[self.__id].dist):
            self.__routingMap[senderId] = RoutingMapEntry(routingMap[self.__id].dist, senderId)
            registeredSender = True
        
        if not registeredSender:
            return False
        
        changes = False
        
        deprecated = []
        
        for k in self.__routingMap.keys():
            if self.__routingMap[k].nextHop == senderId and k != senderId and k not in routingMap.keys():
                deprecated.append(k)
        
        for k in deprecated:
            del self.__routingMap[k]
            changes = True
        
        for k in routingMap.keys():
            if k != self.__id and (k not in self.__routingMap or self.__routingMap[k].dist > routingMap[k].dist + self.__routingMap[senderId].dist):
                self.__routingMap[k] = RoutingMapEntry(routingMap[k].dist + self.__routingMap[senderId].dist, senderId)
                changes = True
            
        return changes
    
    def readRoutes(self, edges: list[EdgeMapEntry]):
        """
        Updates the node's routing table based on the direct edges in the network.
        - If some of the current routes are no longer reachable, the node removes them.
        - The node updates its routes if some paths have not been added yet or if they are better than the current ones.

        Args:
            edges (list[EdgeMapEntry]): A list of edges directly connected to the node.
        """
        entryToDel = []
        for k in self.__routingMap.keys():
            exists = False
            for e in edges:
                if e.dst == self.__routingMap[k].nextHop:
                    exists = True
                    break
            if not exists:
                entryToDel.append(k)
            
        for k in entryToDel:
            del self.__routingMap[k]
            
        for e in edges:
            if e.dst not in self.__routingMap.keys() or self.__routingMap[e.dst].dist > e.w:
                self.__routingMap[e.dst] = RoutingMapEntry(e.w, e.dst)
        
class EdgesMap:
    """
    Represents the entire network topology, managing nodes and edges.

    Attributes:
        __edgeMap (dict[int, list[EdgeMapEntry]]): A mapping of node IDs to their connected edges.
    """
    def __init__(self) -> None:
        """
        Initializes an empty network topology.
        """
        self.__edgeMap: dict[int, list[EdgeMapEntry]] = {}
        
    def __str__(self):
        """
        Returns a string representation of the entire network's edge map.

        Returns:
            str: The edge map as a string showing connections and weights.
        """
        toRet = "Edge Map\n"
        seen = []
        for k in self.__edgeMap.keys():
            for e in self.__edgeMap[k]:
                if (k, e.dst) not in seen and (e.dst, k) not in seen:
                    seen.append((k, e.dst))
                    toRet += f'({k}) -- {e.w} -- ({e.dst})\n'
        return toRet
    
    def doExistsNode(self, nodeId: int) -> bool:
        """
        Checks if a node exists in the network.

        Args:
            nodeId (int): The id of the node to check.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        return nodeId in self.__edgeMap.keys()
    
    def doExistsEdge(self, srcId: int, dstId: int) -> bool:
        """
        Checks if an edge exists between two nodes.

        Args:
            srcId (int): The source node id.
            dstId (int): The destination node id.

        Returns:
            bool: True if the edge exists, False otherwise.
        """
        if srcId not in self.__edgeMap.keys() or dstId not in self.__edgeMap.keys():
            return False
        
        for e in self.__edgeMap[srcId]:
            if e.dst == dstId:
                return True
        
        return False
        
    def addEdge(self, srcId: int, dstId: int, weight: int, NodeList: list[WebNode]):
        """
        Adds an edge between two nodes (if they exist) and make them read their physical connections.

        Args:
            srcId (int): The source node id.
            dstId (int): The destination node id.
            weight (int): The weight of the edge.
            NodeList (list[WebNode]): The list of all nodes in the network.
        """
        if srcId not in self.__edgeMap.keys() or dstId not in self.__edgeMap.keys():
            return
        
        update = False
        
        if not self.doExistsEdge(srcId, dstId):
            self.__edgeMap[srcId].append(EdgeMapEntry(dstId, weight))
            update = True
            
        if not self.doExistsEdge(dstId, srcId):
            self.__edgeMap[dstId].append(EdgeMapEntry(srcId, weight))
            update = True
            
        if update:
            makeNodesReadNet([srcId, dstId], self, NodeList)
    
    def removeEdge(self, srcId: int, dstId: int, NodeList: list[WebNode]):
        """
        Removes an edge between two nodes (if it exists) and make them read their physical connections.

        Args:
            srcId (int): The source node id.
            dstId (int): The destination node id.
            NodeList (list[WebNode]): The list of all nodes in the network.
        """
        if srcId not in self.__edgeMap.keys() or dstId not in self.__edgeMap.keys():
            return
        
        for e in self.__edgeMap[srcId]:
            if e.dst == dstId:
                self.__edgeMap[srcId].remove(e)
                break
            
        for e in self.__edgeMap[dstId]:
            if e.dst == srcId:
                self.__edgeMap[dstId].remove(e)
                break
        
        makeNodesReadNet([srcId, dstId], self, NodeList)
    
    def addNode(self, nodeId: int) -> WebNode:
        """
        Adds a new node to the network if no other node with the same id exists.

        Args:
            nodeId (int): The id of the node to add.

        Returns:
            WebNode: The newly created node, or None if the node already exists.
        """
        if nodeId not in self.__edgeMap.keys():
            self.__edgeMap[nodeId] = []
            return WebNode(nodeId)
        return None
    
    def removeNode(self, nodeId: int, NodeList: list[WebNode]):
        """
        Removes a node and all of its connections from the network and make its neighbors read their physical connections.

        Args:
            nodeId (int): The id of the node to remove.
            NodeList (list[WebNode]): The list of all nodes in the network.
        """
        if nodeId not in self.__edgeMap.keys():
            return
        
        neighbors = self.getNeighborsId(nodeId)
        
        NodeList.remove(NodeList[findNodePos(nodeId, NodeList)])
        
        for k in self.__edgeMap.keys():
            i = 0
            while i in range(len(self.__edgeMap[k])):
                if self.__edgeMap[k][i].dst == nodeId:
                    self.__edgeMap[k].remove(self.__edgeMap[k][i])
                else:
                    i+=1
        del self.__edgeMap[nodeId]
        
        makeNodesReadNet(neighbors, self, NodeList)
    
    def getEdges(self, nodeId: int) -> list[EdgeMapEntry]:
        """
        Retrieves all edges connected to a specific node.

        Args:
            nodeId (int): The id of the node.

        Returns:
            list[EdgeMapEntry]: A list of edges connected to the node.
        """
        return self.__edgeMap[nodeId] if nodeId in self.__edgeMap.keys() else None
    
    def getNeighborsId(self, nodeId: int) -> list[int]:
        """
        Retrieves the ids of all neighboring nodes.

        Args:
            nodeId (int): The id of the node.

        Returns:
            list[int]: A list of neighboring node ids.
        """
        edges = self.getEdges(nodeId)
        nb = []
        for e in edges:
            nb.append(e.dst)
        return nb

def findNodePos(id: int, NodeList: list[WebNode]) -> int:
    """
    Finds the position of a node in the node list.

    Args:
        id (int): The id of the node to find.
        NodeList (list[WebNode]): The list of all nodes.

    Returns:
        int: The index of the node in the list, or None if not found.
    """
    for n in NodeList:
        if n.getId() == id:
            return NodeList.index(n)
    return None

def makeNodesReadNet(nodesId: list[int], NetManager: EdgesMap, NodeList: list[WebNode]):
    """
    Updates the routing tables of specific nodes based on the current network topology.

    Args:
        nodesId (list[int]): A list of node ids to update.
        NetManager (EdgesMap): The network manager containing the edges.
        NodeList (list[WebNode]): The list of all nodes in the network.
    """
    for n in nodesId:
        NodeList[findNodePos(n, NodeList)].readRoutes(NetManager.getEdges(n))

def updateNet(NodeList: list[WebNode], NetManager: EdgesMap, priorityNodesId:list[int] = []):
    """
    Updates the routing tables of all nodes in the network, giving priority to those that are possibly specified.

    Args:
        NodeList (list[WebNode]): The list of all nodes in the network.
        NetManager (EdgesMap): The network manager containing the edges.
        priorityNodesId (list[int], optional): A list of node ids to prioritize for updates.
    """
    queue = []
    
    for id in priorityNodesId:
        queue.append(id)
        
    for wn in NodeList:
        if wn.getId() not in queue:
            queue.append(wn.getId())
    
    changes = True
    while changes:
        changes = False
        for id in queue:
            for nb in NetManager.getNeighborsId(id):
                if NodeList[findNodePos(nb, NodeList)].updateRoutes(id, NodeList[findNodePos(id, NodeList)].getRoutingMap()):
                    changes = True