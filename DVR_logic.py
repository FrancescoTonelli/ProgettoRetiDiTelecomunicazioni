from tabulate import tabulate

class RoutingMapEntry:
    def __init__(self, dist:int, nextHop: int):
        self.dist:int = dist
        self.nextHop:int = nextHop
        
class EdgeMapEntry:
    def __init__(self, dst:int, dist: int):
        self.dst:int = dst
        self.dist:int = dist

class WebNode:
    
    def __init__(self, id:int):
        self.__routingMap:dict[int, RoutingMapEntry] = {}
        self.__id:int = id
        
    def getId(self) -> int:
        return self.__id
    
    def getRoutingMap(self) -> int:
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

    def updateRoutes(self, senderId: int, routingMap: dict[int, RoutingMapEntry]) -> bool:
        
        registeredSender = senderId in self.__routingMap.keys()
        
        if self.__id in routingMap.keys() and (not registeredSender or self.__routingMap[senderId].dist > routingMap[self.__id].dist):
            self.__routingMap[senderId] = RoutingMapEntry(routingMap[self.__id].dist, senderId)
            registeredSender = True
        
        if not registeredSender:
            return False
        
        changes = False
        
        deprecated = []
        
        for k in self.__routingMap.keys():
            if self.__routingMap[k].nextHop == senderId and k != senderId:
                exists = False
                for k1 in routingMap.keys():
                    if k1 == k:
                        exists = True
                        break
                
                if not exists:
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
            if e.dst not in self.__routingMap.keys() or self.__routingMap[e.dst].dist > e.dist:
                self.__routingMap[e.dst] = RoutingMapEntry(e.dist, e.dst)
        
class EdgesMap:
    
    def __init__(self) -> None:
        self.__edgeMap: dict[int, list[EdgeMapEntry]] = {}
        
    def __str__(self):
        toRet = "Edge Map\n"
        for k in self.__edgeMap.keys():
            for e in self.__edgeMap[k]:
              toRet += f'({k}) -- {e.dist} --> ({e.dst})\n'
        return toRet
    
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
        
        makeNodesReadNet([srcId, dstId], self, NodeList)
    
    def addNode(self, nodeId: int) -> WebNode:
        if nodeId not in self.__edgeMap.keys():
            self.__edgeMap[nodeId] = []
            return WebNode(nodeId)
        return None
    
    def removeNode(self, nodeId: int, NodeList: list[WebNode]):
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

def updateNet(NodeList: list[WebNode], NetManager: EdgesMap, priorityNodesId:list[int] = []):
    
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