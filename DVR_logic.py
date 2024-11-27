from tabulate import tabulate
import heapq

class RoutingMapEntry:
    """
    Represents a single entry in the routing table of a node.
    A routing table is a dictionary, where the key is the destination node identifier
    and the value is a RoutingMapEntry object.
    Attributes:
        dist (int): The distance to the destination.
        nextHop (int): The identifier of the next hop node.
    """
    def __init__(self, dist:int, nextHop: int):
        """
        Constructor to initialize a routing table entry.
        Args:
            dist (int): The distance to the destination.
            nextHop (int): The identifier of the next hop node.
        """
        self.dist:int = dist
        self.nextHop:int = nextHop
        
class EdgeMapEntry:
    
    def __init__(self, dst:int, w: int):
        
        self.dst:int = dst
        self.w:int = w

class WebNode:
    
    def __init__(self, id:int):
        
        self.__routingMap:dict[int, RoutingMapEntry] = {}
        self.__id:int = id
        
    def getId(self) -> int:
        
        return self.__id
    
    def getRoutingMap(self) -> dict[int, RoutingMapEntry]:
        
        return self.__routingMap
    
    def __str__(self):
        
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

    def updateRoutes(self, senderId: int, routingMap: dict[int, RoutingMapEntry], phisical:list[EdgeMapEntry]) -> bool:
        actionLog(f"Node {self.__id}: received {senderId}'s table to update")
        registeredSender = senderId in self.__routingMap.keys()
        
        if self.__id in routingMap.keys() and (not registeredSender or self.__routingMap[senderId].dist > routingMap[self.__id].dist):
            messageLog(f"Node {self.__id}: adding sender {senderId}: w:{routingMap[self.__id].dist}, nh:{senderId}")
            self.__routingMap[senderId] = RoutingMapEntry(routingMap[self.__id].dist, senderId)
            registeredSender = True
        
        if not registeredSender:
            messageLog(f"Node {self.__id}: has no route to {senderId}")
            return False
        
        changes = False
        deprecated = []
        
        for k in self.__routingMap.keys():
            if self.__routingMap[k].nextHop == senderId and k != senderId and k not in routingMap.keys():
                messageLog(f"Node {self.__id}: route to {k} deprecated")
                deprecated.append(k)
        
        for k in deprecated:
            updated = False
            for e in phisical:
                if e.dst == k:
                    messageLog(f"Node {self.__id}: updating deprecated route to {k}: w:{e.w}, nh:{e.dst}")
                    self.__routingMap[k] = RoutingMapEntry(e.w, e.dst)
                    updated = True
                    break
            if not updated:
                messageLog(f"Node {self.__id}: removing deprecated route to {k}")
                del self.__routingMap[k]
            changes = True
            
        
        for k in routingMap.keys():
            if k != self.__id and (k not in self.__routingMap or self.__routingMap[k].dist > routingMap[k].dist + self.__routingMap[senderId].dist):
                messageLog(f"Node {self.__id}: updating route to {k}: w:{routingMap[k].dist + self.__routingMap[senderId].dist}, nh:{senderId}")
                self.__routingMap[k] = RoutingMapEntry(routingMap[k].dist + self.__routingMap[senderId].dist, senderId)
                changes = True
        
        if changes:
            messageLog(f"\n{str(self)}\n")
        return changes
    
    def readRoutes(self, edges: list[EdgeMapEntry]):
        messageLog(f"Node {self.__id}: reading routes\n")
        entryToDel = []
        
        for k in self.__routingMap.keys():
            exists = False
            for e in edges:
                if e.dst == self.__routingMap[k].nextHop:
                    if e.w != self.__routingMap[k].dist and e.dst == k:
                        self.__routingMap[k].dist = e.w
                        messageLog(f"Node {self.__id}: found deprecated route to {k}\n")
                        for k1 in self.__routingMap.keys():
                            if self.__routingMap[k1].nextHop == e.dst and k1 not in entryToDel:
                                entryToDel.append(k1)
                    exists = True
                    break
            if not exists and k not in entryToDel:
                entryToDel.append(k)
            
        for k in entryToDel:
            messageLog(f"Node {self.__id}: removing route to {k}\n")
            del self.__routingMap[k]
            
        for e in edges:
            if e.dst not in self.__routingMap.keys() or self.__routingMap[e.dst].dist > e.w:
                messageLog(f"Node {self.__id}: updating route to {e.dst}: w:{e.w}, nh:{e.dst}\n")
                self.__routingMap[e.dst] = RoutingMapEntry(e.w, e.dst)
                
        messageLog(f"\n{str(self)}\n")
        
class EdgesMap:
    
    def __init__(self) -> None:
        
        self.__edgeMap: dict[int, list[EdgeMapEntry]] = {}
        
    def __str__(self):
        
        toRet = "Edge Map\n"
        seen = []
        for k in self.__edgeMap.keys():
            for e in self.__edgeMap[k]:
                if (k, e.dst) not in seen and (e.dst, k) not in seen:
                    seen.append((k, e.dst))
                    toRet += f'({k}) -- {e.w} -- ({e.dst})\n'
        return toRet
    
    def getMap(self) -> dict[int, list[EdgeMapEntry]]:
        
        return self.__edgeMap
    
    def doExistsNode(self, nodeId: int) -> bool:
        
        return nodeId in self.__edgeMap.keys()
    
    def doExistsEdge(self, srcId: int, dstId: int) -> bool:
        
        if srcId not in self.__edgeMap.keys() or dstId not in self.__edgeMap.keys():
            return False
        
        for e in self.__edgeMap[srcId]:
            if e.dst == dstId:
                return True
        
        return False
        
    def addEdge(self, srcId: int, dstId: int, weight: int, NodeList: list[WebNode]):
        
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
            actionLog(f"Edge {srcId} - {dstId} added")
            makeNodesReadNet([srcId, dstId], self, NodeList)
    
    def removeEdge(self, srcId: int, dstId: int, NodeList: list[WebNode]):
        
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
        actionLog(f"Edge {srcId} - {dstId} removed")
        makeNodesReadNet([srcId, dstId], self, NodeList)
    
    def addNode(self, nodeId: int) -> WebNode:
        
        if nodeId not in self.__edgeMap.keys():
            actionLog(f"Node {nodeId} added")
            self.__edgeMap[nodeId] = []
            return WebNode(nodeId)
        return None
    
    def removeNode(self, nodeId: int, NodeList: list[WebNode]):
        
        if nodeId not in self.__edgeMap.keys():
            return
        
        neighbors = self.getNeighborsId(nodeId)
        
        actionLog(f"Node {nodeId} removed")
        
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
        
        return self.__edgeMap[nodeId] if nodeId in self.__edgeMap.keys() else None
    
    def getNeighborsId(self, nodeId: int) -> list[int]:
        
        edges = self.getEdges(nodeId)
        nb = []
        for e in edges:
            nb.append(e.dst)
        return nb

def findNodePos(id: int, NodeList: list[WebNode]) -> int:
    
    for n in NodeList:
        if n.getId() == id:
            return NodeList.index(n)
    return None

def makeNodesReadNet(nodesId: list[int], NetManager: EdgesMap, NodeList: list[WebNode]):
    
    for n in nodesId:
        NodeList[findNodePos(n, NodeList)].readRoutes(NetManager.getEdges(n))

def updateNet(NodeList: list[WebNode], NetManager: EdgesMap, priorityNodesId:list[int]):
    
    changes = True
    while changes:
        queue = priorityNodesId[:]
        
        changes = False
        while queue:
            id = queue.pop(0)
            for nb in NetManager.getNeighborsId(id):
                if NodeList[findNodePos(nb, NodeList)].updateRoutes(id, NodeList[findNodePos(id, NodeList)].getRoutingMap(), NetManager.getEdges(nb)):
                    queue.append(nb)
                    changes = True
                    
def actionLog(message: str):
    
        maxLen = 60 - len(message)
        sep = "-" * (maxLen // 2)
        with open('log.txt', 'a') as log:
            log.write(f"\n{sep} {message} {sep}\n")
            
def messageLog(message: str):
    
    with open('log.txt', 'a') as log:
        log.write(f"{message}\n")

#Test
def dijkstra(graph: dict[int, list[EdgeMapEntry]], start: int) -> dict[int, int]:
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_distance > distances[current_node]:
            continue
        
        for edge in graph[current_node]:
            distance = current_distance + edge.w
            
            if distance < distances[edge.dst]:
                distances[edge.dst] = distance
                heapq.heappush(priority_queue, (distance, edge.dst))
    
    return distances

def is_minimum_distance(graph: dict[int, list[EdgeMapEntry]], node1: int, node2: int, distance: int) -> bool:
    distances = dijkstra(graph, node1)
    return distances[node2] == distance