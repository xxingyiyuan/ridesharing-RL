from route import Route


class Packing:
    def __init__(self, driver):
        self.driver = driver
        self.passengers = []

    def getDriver(self):
        return self.driver

    def getPassengers(self):
        return self.passengers

    def getBudget(self):
        budget = 0
        for p in self.passengers:
            budget += p.budget
        return budget

    def getWeight(self):
        return self.getBudget() - self.driver.askPrice

    def isFeasible(self):
        # budget constraint
        if self.getWeight() < 0:
            return False
        # binary constraint
        for p in self.passengers:
            if p.isSelect():
                return False
        if self.driver.sPassengerNum > 0:
            return False
        return True

    def tryAddPassengers(self, passVec):
        # capacity constraint
        reqSeats = 0
        for p in passVec:
            reqSeats += p.getRequiredSeats()
        if reqSeats > self.driver.getAvaliableSeats():
            return False

        route = Route(self.driver)
        for p in passVec:
            # waitTime、detour constraint
            if not route.addPassenger(p):
                return False
        self.passengers = passVec
        return True
