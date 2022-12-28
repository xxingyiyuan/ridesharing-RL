import time
from auctioneer import Auctioneer
from coalition import Coalition
from passenger import Passenger
from driver import Driver
from tool import Tool
from demand import Demand


class AlgorithmCFA:
    def __init__(self, driSet, dcaMat, passSet, pcaMat):
        self.driList = driSet
        self.dcaMat = dcaMat
        self.passList = passSet
        self.pcaMat = pcaMat

        # initialize a coalition for each driver
        self.coalitions = {}
        for d in self.driList:
            self.coalitions[d.id] = Coalition(d)
        self.auctioneer = Auctioneer(self.driList, self.coalitions)
        start = time.clock()
        self.run()
        end = time.clock()
        self.runningTime = end - start

    def run(self):
        self.initAllocation()

        while True:
            tmp = self.opt
            for p in self.passList:
                # driVec: candidate drivers for passenger p
                driVec = self.pcaMat[p.id - 1]
                if len(driVec) == 0:
                    continue
                if p.isSelect():
                    self.inGroupBranch(p, driVec)
                else:
                    self.notInGroupBranch(p, driVec)
            if self.opt - tmp < 1:
                break

    def collectData(self):
        res = [0]*5
        for coalition in self.coalitions.values():

            for p in coalition.curPassengers:
                res[0] += p.getUtility()
                if p.isWin:
                    res[1] += 1
            d = coalition.getDriver()
            res[2] += d.getUtility()
            if d.isWin:
                res[3] += 1
        res[4] = self.runningTime
        return res

    def initAllocation(self):
        # find a suitable driver for each passenger
        for p in self.passList:
            driver = self.findDriverByOrgDist(p)
            if driver:
                coalition = self.coalitions[driver.id]
                coalition.addPassenger(p)
        self.opt = self.auctioneer.auction()

    def findDriverByOrgDist(self, passenger: Passenger) -> Driver:
        """find best driver for passenger

        Args:
            passenger (Passenger): _description_

        Returns:
            Driver: the best driver for passenger
        """
        driVec = self.pcaMat[passenger.id - 1]
        bestDriver = None
        minDist = float('inf')
        for d in driVec:
            coalition = self.coalitions[d.id]
            if coalition.tryAddPassenger(passenger):
                originDist = Tool.calNodeDist(passenger.getOrg(), d.getOrg())
                if originDist < minDist:
                    minDist = originDist
                    bestDriver = d
        return bestDriver

    def inGroupBranch(self, passenger, driVec):
        # source coalition
        srcCoalition = self.coalitions[passenger.driverId]
        tmp = self.opt

        isLeave = False
        srcCoalition.removePassenger(passenger)
        cur = self.auctioneer.auction()
        if cur > tmp:
            tmp = cur
            isLeave = True

        targeCoalition = None
        for d in driVec:
            if srcCoalition.id == d.id:
                continue
            coalition = self.coalitions[d.id]

            if coalition.addPassenger(passenger):
                cur = self.auctioneer.auction()
                if cur > tmp:
                    tmp = cur
                    targeCoalition = coalition
                # restore
                coalition.removePassenger(passenger)

        # switch operation
        if targeCoalition:
            targeCoalition.addPassenger(passenger)
        elif not isLeave:
            srcCoalition.addPassenger(passenger)
        self.auctioneer.auction()
        self.opt = tmp

    def notInGroupBranch(self, passenger, driVec):
        targeCoalition = None
        tmp = self.opt
        # find the driver to make max increasement
        for d in driVec:
            coalition = self.coalitions[d.id]
            if coalition.addPassenger(passenger):
                cur = self.auctioneer.auction()
                if cur > tmp:
                    tmp = cur
                    targeCoalition = coalition
                # restore
                coalition.removePassenger(passenger)

        # join operation
        if targeCoalition:
            targeCoalition.addPassenger(passenger)
            self.opt = self.auctioneer.auction()

    def getTotalUtility(self):
        res = 0
        for coalition in self.coalitions.values():
            for p in coalition.curPassengers:
                res += p.getUtility()
        return res


if __name__ == '__main__':
    drivers_demand, passengers_demand = Demand.loadDemand('beijing', 0, 5, 0.5)
    drivers, dcaMat, passengers, pcaMat = Demand.initParticipants(
        drivers_demand, passengers_demand)
    CFA = AlgorithmCFA(drivers, dcaMat, passengers, pcaMat)
    print(CFA.collectData())
