from auctioneer import Auctioneer
from coalition import Coalition
from packing import Packing
import time


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
        start = time.clock()
        self.run()
        end = time.clock()
        self.runningTime = end - start
        # print('alogrithm TSG: ', self.getTotalUtility())

    def run(self):
        # stage 1:
        candidatePackings = self.findPackings()
        # reverse:True 降序
        candidatePackings.sort(
            key=lambda packing: packing.getWeight(), reverse=True)
        while len(candidatePackings):
            pack = candidatePackings.pop(0)
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

    def collectData(self):
        res = [0]*5
        for p in self.passList:
            res[0] += p.getUtility()
            if p.isWin:
                res[1] += 1
        for d in self.driList:
            res[2] += d.getUtility()
            if d.isWin:
                res[3] += 1
        res[4] = self.runningTime
        return res

    def getTotalUtility(self):
        res = 0
        for coalition in self.coalitions.values():
            for p in coalition.curPassengers:
                res += p.getUtility()
        return res
