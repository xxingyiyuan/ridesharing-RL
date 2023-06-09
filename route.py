from passenger import Passenger
from tool import Tool
from node import Node
from driver import Driver
from settings import SPEED


class Route:
    def __init__(self, dri: 'Driver'):
        self.driver = dri  # The driver
        self.nodePath = []  # The node sequence in route
        self.mkey = 1  # the index of a node, self.mkey -> node.who, indicates which passenger the node belongs to
        self.idxMap = {}  # key: self.mkey, value: the passenger corresponding to self.mkey
        # The container storing the distance of share trip for driver (key = 0) and passengers (key > 0)
        self.sDistMap = None

        src = Node(0, 0, dri.getOrg(), 0)
        if self.driver.isVocational:
            # 职业司机的终点为虚拟节点，与前面节点之间的距离为0
            dst = Node(0, 1, dri.getDst(), 0)
        else:
            dst = Node(0, 1, dri.getDst(), Tool.calNodeDist(
                dri.getOrg(), dri.getDst()))
        self.nodePath.append(src)
        self.nodePath.append(dst)

    def addPassenger(self, passenger) -> bool:
        # Find the feasible insertion positions for source
        srcIdxVec = []
        self.findSourceInsertion(passenger, srcIdxVec)
        if len(srcIdxVec) == 0:
            return False
        # Find the feasible insertion positions for destination
        dstIdxMat = []
        self.findDestinationInsertion(passenger, srcIdxVec, dstIdxMat)

        isQuit = True
        for dstIdxVec in dstIdxMat:
            if len(dstIdxVec) != 0:
                isQuit = False
                break
        # if there is not exist feasible insertion, isQuit = true
        if isQuit:
            return False

        # Get the best insertion position to obtain minimum distance
        min_dist = float('inf')
        for i, dstIdxVec in enumerate(dstIdxMat):
            for dstIdx in dstIdxVec:
                sDistMap = self.calShareDistances(
                    passenger, srcIdxVec[i], dstIdx)
                if sDistMap[0] < min_dist:
                    min_dist = sDistMap[0]
                    src = srcIdxVec[i]
                    dst = dstIdx
        self.updateRoute(passenger, src, dst)
        return True

    def findSourceInsertion(self, passenger, srcIdxVec: list):
        for i in range(1, len(self.nodePath)):
            if self.insertSource(passenger, i):
                srcIdxVec.append(i)

    def insertSource(self, passenger: 'Passenger', srcIdx) -> bool:
        dist = 0  # the distance bwtween the origin node of driver and current node
        distMap = {}
        isVocational = self.driver.isVocational
        for i, node in enumerate(self.nodePath[1:], start=1):
            # update dist
            if i != srcIdx:
                dist += node.pcDist
            else:
                dist += Tool.calNodeDist(
                    self.nodePath[i - 1].coordinate, passenger.getOrg())
                # check waitTime constraint for the new passenger
                if (dist/SPEED - passenger.getWaitTime()) > 0:
                    return False
                if isVocational and node.who == 0 and node.where == 1:
                    # 职业司机的虚拟终点
                    dist += 0
                else:
                    dist += Tool.calNodeDist(passenger.getOrg(),
                                             node.coordinate)

            # node.where = 0: an origin node, check waitTime constraint for other passengers
            if node.where == 0:
                if (dist/SPEED - self.idxMap[node.who].getWaitTime()) > 0:
                    return False
                # store the distance between the origin of driver and the origin of a passenger
                distMap[node.who] = dist
            # node.where = 1: a destination node, check detour constraint for participants
            else:
                # node.who == 0: it must be the destination node of driver, check detour constraint for the driver
                if node.who == 0:
                    # 只考虑兼职司机的绕路约束
                    if not isVocational and (dist - self.driver.iDist*(1+self.driver.getDetourRatio())) > 0:
                        return False
                # check detour constraint for other passengers
                else:
                    p = self.idxMap[node.who]
                    # dist - distMap[node.who]: the shared trip distance of p
                    if (dist - distMap[node.who] - p.iDist * (1+p.getDetourRatio())) > 0:
                        return False
        return True

    def findDestinationInsertion(self, passenger: 'Passenger', srcIdxVec: int, dstIdxMat: list):
        for srcIdx in srcIdxVec:
            dstIdxVec = []
            for dstIdx in range(srcIdx, len(self.nodePath)):
                if self.insertDestination(passenger, srcIdx, dstIdx):
                    dstIdxVec.append(dstIdx)
            dstIdxMat.append(dstIdxVec)

    def insertDestination(self, passenger: 'Passenger', srcIdx, dstIdx) -> bool:
        dist = 0  # the distance bewteen the origin of driver and current node
        passDist = 0  # the shared trip distance of passenger: check detour constraint for passenger
        isInsert = False  # i == srcIdx: True, i == dstIdx: False
        distMap = {}
        isVocational = self.driver.isVocational
        for i, node in enumerate(self.nodePath[1:], start=1):
            # update dist
            if i == srcIdx and i == dstIdx:
                if isVocational and node.who == 0 and node.where == 1:
                    dist += Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getOrg(
                    )) + passenger.iDist
                else:
                    dist += Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getOrg(
                    )) + passenger.iDist + Tool.calNodeDist(passenger.getDst(), node.coordinate)
            elif i == srcIdx:
                dist += Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getOrg(
                )) + Tool.calNodeDist(passenger.getOrg(), node.coordinate)
                isInsert = True
            elif i == dstIdx:
                if isVocational and node.who == 0 and node.where == 1:
                    dist += Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getDst(
                    ))
                else:
                    dist += Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getDst(
                    )) + Tool.calNodeDist(passenger.getDst(), node.coordinate)
            else:
                if isVocational and node.who == 0 and node.where == 1:
                    dist += 0
                else:
                    dist += node.pcDist

            if isInsert:
                if i == srcIdx:
                    passDist += Tool.calNodeDist(passenger.getOrg(),
                                                 node.coordinate)
                elif i == dstIdx:
                    passDist += Tool.calNodeDist(
                        self.nodePath[i-1].coordinate, passenger.getDst())
                    # check detour constraint for passenger
                    if passDist - passenger.iDist*(1+passenger.getDetourRatio()) > 0:
                        return False
                    isInsert = False
                else:
                    passDist += node.pcDist

            # check waittime constraint for other passengers
            if node.where == 0:
                if (dist/SPEED - self.idxMap[node.who].getWaitTime()) > 0:
                    return False
                distMap[node.who] = dist
            else:
                # node.where == 1
                if node.who == 0:
                    # check detour constraint for part-time driver
                    if not isVocational and (dist - self.driver.iDist*(1+self.driver.getDetourRatio())) > 0:
                        return False
                else:
                    p = self.idxMap[node.who]
                    # check detour constraint for other passengers
                    # dist - distMap[node.who]: the shared trip distance of p
                    if (dist - distMap[node.who] - p.iDist * (1+p.getDetourRatio())) > 0:
                        return False
        return True

    def calShareDistances(self, passenger: 'Passenger', srcIdx, dstIdx) -> dict:
        isAddMap = {0: True}  # 0 for driver
        # key: driver (key = 0) and passengers (key > 0), value: the distance of share trip
        sDistMap = {0: 0}
        passDist = 0  # the shared trip distance of new passenger
        isUpdate = False
        isVocational = self.driver.isVocational
        for i, node in enumerate(self.nodePath[1:], start=1):
            tmp = 0  # the distance between the previous node and current node
            if i == srcIdx and i == dstIdx:
                if isVocational and node.who == 0 and node.where == 1:
                    tmp = Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getOrg(
                    )) + passenger.iDist
                else:
                    tmp = Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getOrg(
                    )) + passenger.iDist + Tool.calNodeDist(passenger.getDst(), node.coordinate)
                isUpdate = True
            elif i == srcIdx:
                tmp = Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getOrg(
                )) + Tool.calNodeDist(passenger.getOrg(), node.coordinate)
                isUpdate = True
            elif i == dstIdx:
                if isVocational and node.who == 0 and node.where == 1:
                    tmp = Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getDst(
                    ))
                else:
                    tmp = Tool.calNodeDist(self.nodePath[i-1].coordinate, passenger.getDst(
                    )) + Tool.calNodeDist(passenger.getDst(), node.coordinate)
            else:
                if isVocational and node.who == 0 and node.where == 1:
                    tmp = 0
                else:
                    tmp = node.pcDist

            # isUpdate: True for i = srcIdx, False for i = dstIdx
            # passDist: the shared trip distance of new passenger
            if isUpdate:
                if i == srcIdx and i == dstIdx:
                    passDist = passenger.iDist
                    isUpdate = False
                elif i == srcIdx:
                    passDist += Tool.calNodeDist(passenger.getOrg(),
                                                 node.coordinate)
                elif i == dstIdx:
                    passDist += Tool.calNodeDist(
                        self.nodePath[i-1].coordinate, passenger.getDst())
                    isUpdate = False
                else:
                    passDist += tmp

            # compute the shared trip distance for participants
            for key in sDistMap.keys():
                if(isAddMap[key]):
                    sDistMap[key] += tmp
            #
            if node.where == 0:
                isAddMap[node.who] = True
                sDistMap[node.who] = 0
            else:
                isAddMap[node.who] = False

        sDistMap[self.mkey] = passDist
        return sDistMap

    def updateRoute(self, passenger: 'Passenger', srcIdx, dstIdx):
        self.sDistMap = self.calShareDistances(passenger, srcIdx, dstIdx)
        isVocational = self.driver.isVocational
        # update the PrCuDistance of nodePath[src] and nodePath[dst]
        srcNode = self.nodePath[srcIdx]
        srcNode.pcDist = Tool.calNodeDist(
            passenger.getOrg(), srcNode.coordinate)
        dstNode = self.nodePath[dstIdx]
        if isVocational and dstNode.who == 0 and dstNode.where == 1:
            dstNode.pcDist = 0
        else:
            dstNode.pcDist = Tool.calNodeDist(
                passenger.getDst(), dstNode.coordinate)

        # insert destination node at dstIdx in nodePath
        if srcIdx == dstIdx:
            self.nodePath.insert(dstIdx, Node(
                self.mkey, 1, passenger.getDst(), passenger.iDist))
        else:
            self.nodePath.insert(dstIdx, Node(self.mkey, 1, passenger.getDst(
            ), Tool.calNodeDist(self.nodePath[dstIdx-1].coordinate, passenger.getDst())))
        # insert origin node at srcIdx in nodePath
        self.nodePath.insert(srcIdx, Node(self.mkey, 0, passenger.getOrg(
        ), Tool.calNodeDist(self.nodePath[srcIdx-1].coordinate, passenger.getOrg())))

        # add the new passenger
        self.idxMap[self.mkey] = passenger
        self.mkey += 1

    def updateSharedDist(self):
        if len(self.idxMap):
            for mkey, p in self.idxMap.items():
                p.sDist = self.sDistMap[mkey]
            self.driver.sDist = self.sDistMap[0]
        # no passengers
        else:
            self.driver.sDist = 0


if __name__ == '__main__':
    driDemand = (116.43844, 39.85513, 116.42189, 39.91666, 5, 0.5)
    driver = Driver(33, driDemand)
    route1 = Route(driver)
    route2 = Route(driver)
    print(route1 == route2) // False
    print(route1.driver == route2.driver) // True
