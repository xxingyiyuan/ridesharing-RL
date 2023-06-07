import time
from auctioneer import Auctioneer
from coalition import Coalition
from passenger import Passenger
from driver import Driver
from settings import PRICE_PER_KILOMETER, PRICE_PER_MINUTE, DISTCOUNT


class AlgorithmDiDi:
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
        # print('alogrithm DiDi: ', self.getTotalUtility())

    def run(self):
        self.didiMatching()
        self.pricing()

    def didiMatching(self):
        # find a suitable driver for each passenger
        for p in self.passList:
            driver = self.findBestDriver(p)
            if driver:
                coalition = self.coalitions[driver.id]
                coalition.addPassenger(p)

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
        minPassDist = float('inf')
        for d in driVec:
            coalition = self.coalitions[d.id]
            if coalition.addPassenger(passenger):
                passDist = passenger.sDist
                if passDist < minPassDist:
                    minPassDist = passDist
                    bestDriver = d
                coalition.removePassenger(passenger)
        return bestDriver

    def pricing(self):
        for coalition in self.coalitions.values():
            driver = coalition.getDriver()
            curPassengers = coalition.curPassengers

            discount = 0.9 if len(curPassengers) > 1 else 1
            # check detour constraint for driver
            if len(curPassengers) == 0 or driver.sDist > (1 + driver.getDetourRatio())*driver.iDist:
                self.determineRoles(coalition, False)
            else:
                # pricing
                totalPayment = 0
                flag = True
                for p in curPassengers:
                    payment = (p.sDist*PRICE_PER_KILOMETER +
                               p.getTime(p.sDist)*PRICE_PER_MINUTE)*discount
                    if p.budget < payment:
                        flag = False
                        break
                    p.payment = payment
                    totalPayment += p.payment
                # result
                if flag:
                    driver.payoff = totalPayment
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

        if not isWin:
            driver.payoff = 0

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
