from route import Route
from driver import Driver
from passenger import Passenger
from tool import Tool
import settings


class Coalition:
    def __init__(self, driver: 'Driver'):
        self.id = driver.id
        self.driver = driver
        # use for checking waitTime and detour constraints and updating shared distance
        self.route = Route(driver)
        self.curPassengers = []

    def getUnitBid(self):
        unitBid = 0
        if len(self.curPassengers):
            passengerBids = [p.budget for p in self.curPassengers]
            unitBid = min(passengerBids)
        return unitBid

    def getPassengerNum(self):
        return len(self.curPassengers)

    def addPassenger(self, passenger: 'Passenger') -> bool:
        # radium constraint
        if Tool.calNodeDist(self.driver.getOrg(), passenger.getOrg()) > settings.RADIUS:
            return False
        # capacity constraint
        if self.driver.getAvaliableSeats() < passenger.getRequiredSeats():
            return False
        # add passenger
        if self.route.addPassenger(passenger):
            self.curPassengers.append(passenger)
            self.updateParticipantInfos(passenger, 1)
            return True
        else:
            return False

    def removePassenger(self, passenger: 'Passenger'):
        self.curPassengers.remove(passenger)
        new_route = Route(self.driver)
        for p in self.curPassengers:
            new_route.addPassenger(p)
        self.route = new_route  # update route
        self.updateParticipantInfos(passenger, 0)

    def updateParticipantInfos(self, passenger: 'Passenger', flag):
        # update shared distance passengers and driver
        self.route.updateSharedDist()
        # flag: 1 for add passenger
        if flag:
            # udpate shared seat and passenger numbers for driver, driverId for passenger
            self.driver.sSeatNum += passenger.getRequiredSeats()
            self.driver.sPassengerNum += 1
            passenger.driverId = self.driver.id
        # flag: 0 for remove passenger
        else:
            self.driver.sSeatNum -= passenger.getRequiredSeats()
            self.driver.sPassengerNum -= 1
            passenger.driverId = 0
            passenger.sDist = 0


if __name__ == '__main__':
    driDemand = (116.43844, 39.85513, 116.42189, 39.91666, 5, 0.5)
    driver = Driver(33, driDemand)
    coalition = Coalition(driver)
    passDemands = [(116.43155, 39.85104, 116.42982, 39.90776, 2, 0.5, 2),
                   (116.43562, 39.85657, 116.41099, 39.8842, 1, 0.5, 2),
                   (116.43633, 39.85484, 116.42318, 39.90946, 2, 0.5, 2)
                   ]
    ids = [10, 82, 101]
    passengers = [Passenger(id, de) for id, de in zip(ids, passDemands)]
    for p in passengers:
        coalition.addPassenger(p)
    for p in passengers:
        print(p)
