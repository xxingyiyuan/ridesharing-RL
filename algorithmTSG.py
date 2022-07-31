from auctioneer import Auctioneer
from coalition import Coalition
from packing import Packing
from passenger import Passenger
from driver import Driver
from tool import Tool


class AlgorithmTSG:
    def __init__(self, driSet, dcaMat, passSet, pcaMat):
        self.driList = driSet
        self.dcaMat = dcaMat
        self.passList = passSet
        self.pcaMat = pcaMat
        self.coalitions = {}
        for d in self.driList:
            self.coalitions[d.id] = Coalition(d)
        self.auctioneer = Auctioneer(self.driList, self.coalitions)
        self.run()

    def run(self):
        # stage 1:
        candidatePackings = self.findPackings()
        # reverse:True 降序
        candidatePackings.sort(
            key=lambda packing: packing.getWeight(), reverse=True)
        for pack in candidatePackings:
            if pack.isFeasible():
                coalition = self.coalitions[pack.getDriver().id]
                for p in pack.getPassengers():
                    coalition.addPassenger(p)

        # stage 2:
        for p in self.passList:
            if p.isSelect():
                continue
            driVec = self.pcaMat[p.id - 1]
            for d in driVec:
                coalition = self.coalitions[d.id]
                if coalition.addPassenger(p):
                    break
        self.opt = self.auctioneer.auction2()

    def findPackings(self):
        candidatePackings = []
        for d in self.driList:
            passVec = self.dcaMat[d.id - 1]
            passNum = len(passVec)
            for i in range(passNum):
                for j in range(i+1, passNum):
                    pack = Packing(d)
                    tmpPassengers = [passVec[i], passVec[j]]
                    if pack.tryAddPassengers(tmpPassengers):
                        candidatePackings.append(pack)
        return candidatePackings

    def getTotalUtility(self):
        return self.opt
