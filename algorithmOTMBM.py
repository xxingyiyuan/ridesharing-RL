from auctioneer import Auctioneer
from coalition import Coalition
from passenger import Passenger
from driver import Driver
from tool import Tool
from settings import SPEED, PRICE_PER_KILOMETER, PRICE_PER_MINUTE, DISTCOUNT


class AlgorithmOTMBM:
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
        self.oneToManyMatching()
        self.pricing()
        # print('alogrithm OTMM: ', self.getTotalUtility())

    def oneToManyMatching(self):
        # (passenger ID, driver ID)
        D = []
        for d in self.driList:
            bestP = self.findBestPassenger(d)
            if bestP is None:
                continue
            bestD = self.findBestDriver(bestP)
            if bestD.id == d.id:
                D.append((bestP.id, bestD.id))

        # stage 1
        for passId, driId in D:
            coalition = self.coalitions[driId]
            p = self.passList[passId - 1]
            coalition.addPassenger(p)
        # stage 2
        while len(D) > 0:
            passId, driId = D.pop(0)
            passVec = self.dcaMat[driId - 1]
            for p in passVec:
                if p.isSelect():
                    continue
                bestD = self.findBestDriver(p)
                if bestD is None:
                    continue
                bestP = self.findBestPassenger(bestD)
                if bestP.id == p.id:
                    coalition = self.coalitions[bestD.id]
                    coalition.addPassenger(bestP)
                    D.append((bestP.id, bestD.id))

    def findBestDriver(self, passenger: Passenger) -> Driver:
        """find best driver for passenger

        Args:
            passenger (Passenger): _description_

        Returns:
            Driver: the best driver for passenger
        """
        # candidate drivers for current passenger
        driVec = self.pcaMat[passenger.id - 1]
        bestDriver = None
        minIncreDist = float('inf')
        for d in driVec:
            coalition = self.coalitions[d.id]
            oldDist = d.getCurDist()
            if coalition.addPassenger(passenger):
                increDist = d.getCurDist() - oldDist
                if increDist < minIncreDist:
                    minIncreDist = increDist
                    bestDriver = d
                coalition.removePassenger(passenger)
        return bestDriver

    def findBestPassenger(self, driver: Driver) -> Passenger:
        passVec = self.dcaMat[driver.id - 1]
        coalition = self.coalitions[driver.id]
        bestPassenger = None
        minIncreDist = float('inf')
        oldDist = driver.getCurDist()
        for p in passVec:
            if p.isSelect():
                continue
            if coalition.addPassenger(p):
                increDist = driver.getCurDist() - oldDist
                if increDist < minIncreDist:
                    minIncreDist = increDist
                    bestPassenger = p
                coalition.removePassenger(p)
        return bestPassenger

    def pricing(self):
        for coalition in self.coalitions.values():
            driver = coalition.getDriver()
            curPassengers = coalition.curPassengers
            flag = True
            totalPayment = 0
            for p in curPassengers:
                payment = (p.sDist*PRICE_PER_KILOMETER +
                           p.getTime(p.sDist)*PRICE_PER_MINUTE)*DISTCOUNT
                if p.budget < payment:
                    flag = False
                    break
                totalPayment += payment
                p.payment = payment

            if flag and totalPayment >= driver.askPrice:
                self.determineRoles(coalition, True)
            else:
                self.determineRoles(coalition, False)

    def determineRoles(self, coalition: Coalition, isWin: bool):
        # result of passenger
        curPassengers = coalition.curPassengers
        for p in curPassengers:
            p.isWin = isWin
            if not isWin:
                p.payment = 0
        # result of driver
        driver = coalition.getDriver()
        driver.isWin = isWin
        if isWin:
            driver.payoff = driver.askPrice

    def getTotalUtility(self):
        res = 0
        for coalition in self.coalitions.values():
            for p in coalition.curPassengers:
                res += p.getUtility()
        return res
