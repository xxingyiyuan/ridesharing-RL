from settings import RATIO_EXCLUDE_PLATFORM_CHARGE


class Auctioneer:
    # The auctioneer determines winning passengers and drivers, then returns matching result, payoffs and payments.
    def __init__(self, drivers: list, coalitions: dict):
        self.drivers = drivers
        self.coalitions = coalitions

    def auction(self):
        # sort coalitions by unitBid in descending order
        # reverse=True: descending order
        coalitions, drivers = self.coalitions, self.drivers
        tmp_coalitions = list(coalitions.values())
        tmp_coalitions.sort(
            key=lambda coalition: coalition.getUnitBid(), reverse=True)
        coalitionNum = len(coalitions)
        for i, coalition in enumerate(tmp_coalitions):
            dri = drivers[coalition.id - 1]
            payoff = 0
            unitPayment = 0
            passNum = coalition.getPassengerNum()
            # lose
            if coalition.getUnitBid()*passNum*RATIO_EXCLUDE_PLATFORM_CHARGE < dri.askPrice:
                self.updateResult((coalition, dri),
                                  (unitPayment, payoff), False)
                continue
            # determine payments and payoffs
            for j in range(i+1, coalitionNum):
                unitBid = tmp_coalitions[j].getUnitBid()
                if unitBid*passNum*RATIO_EXCLUDE_PLATFORM_CHARGE >= dri.askPrice:
                    unitPayment = unitBid
                else:
                    break
            if unitPayment:
                payoff = dri.askPrice
                self.updateResult((coalition, dri),
                                  (unitPayment, payoff), True)
            else:
                self.updateResult((coalition, dri),
                                  (unitPayment, payoff), False)
        return self.getTotalUtility()

    def auction2(self):
        drivers, coalitions = self.exclude()
        drivers.sort(key=lambda driver: driver.askPrice / driver.sPassengerNum)
        coalitions.sort(
            key=lambda coalition: coalition.getUnitBid(), reverse=True)
        size = len(drivers)
        k = -1
        for i in range(size):
            if coalitions[i].getUnitBid() * RATIO_EXCLUDE_PLATFORM_CHARGE >= drivers[i].askPrice / drivers[i].sPassengerNum:
                k = i
            else:
                break
        if k > 0:
            alpha = k
            beta = k
            for i in range(alpha + 1, size):
                if coalitions[i].getUnitBid() * RATIO_EXCLUDE_PLATFORM_CHARGE >= drivers[k].askPrice / drivers[k].sPassengerNum:
                    alpha = i
            for i in range(beta + 1, size):
                if coalitions[k].getUnitBid() * RATIO_EXCLUDE_PLATFORM_CHARGE >= drivers[i].askPrice / drivers[i].sPassengerNum:
                    beta = i
            if self.countWinner(drivers, coalitions, alpha, k) > self.countWinner(drivers, coalitions, k, beta):
                self.determineWinner(drivers, coalitions, alpha, k)
            else:
                self.determineWinner(drivers, coalitions, k, beta)
        else:
            self.determineWinner(drivers, coalitions, 0, 0)
        return self.getTotalUtility()

    def exclude(self):
        drivers, coalitions = self.drivers, list(self.coalitions.values())
        newDrivers, newCoalitions = [], []
        nums = len(drivers)
        for i in range(nums):
            driver = drivers[i]
            coalition = coalitions[i]
            if driver.sPassengerNum == 0:
                continue
            elif coalition.getUnitBid()*coalition.getPassengerNum()*RATIO_EXCLUDE_PLATFORM_CHARGE < driver.askPrice:
                continue
            else:
                newDrivers.append(driver)
                newCoalitions.append(coalition)
        return newDrivers, newCoalitions

    def countWinner(self, drivers, coalitions, b, s):
        count = 0
        driverMap = {}
        for i in range(s):
            driverMap[drivers[i].id] = drivers[i]
        for i in range(b):
            if coalitions[i].id in driverMap:
                count += 1
        return count

    def determineWinner(self, drivers, coalitions, b, s):
        driverMap = {}
        unitPayment = coalitions[b].getUnitBid()
        for i in range(s):
            driverMap[drivers[i].id] = drivers[i]
        for i in range(b):
            driver = coalitions[i].getDriver()
            if driver.id in driverMap:
                self.updateResult(
                    (coalitions[i], driver), (unitPayment, driver.askPrice), True)
            else:
                self.updateResult((coalitions[i], driver), (0, 0), False)

    def updateResult(self, participants: tuple, price: tuple, isWin: bool):
        # participants: (coalition, driver), price: (unitPayment, payoff), isWin
        coalition, driver = participants
        unitPayment, payoff = price
        # update passengers
        for p in coalition.curPassengers:
            p.isWin = isWin
            p.payment = unitPayment

        # update driver
        driver.isWin = isWin
        driver.payoff = payoff

    def getTotalUtility(self):
        res = 0
        for coalition in self.coalitions.values():
            for p in coalition.curPassengers:
                res += p.getUtility()
        return res
