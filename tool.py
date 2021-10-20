import math
import numpy as np
from settings import SPEED, RADIUS


class Tool:
    @classmethod
    def calNodeDist(cls, coordinate1, coordinate2) -> float:
        return math.sqrt(
            math.pow((coordinate1[0] - coordinate2[0]) / 0.00001, 2) +
            math.pow((coordinate1[1] - coordinate2[1]) / 0.00001, 2)
        ) / 1000

    @classmethod
    def getCandidateActions(cls, driList, passList):
        M = len(driList) + 1
        n = len(passList)
        candidateActions = [M*i for i in range(n)]
        # candidateActions = []
        cadidateTable = []
        for i, passenger in enumerate(passList):
            canDri = []
            for j, driver in enumerate(driList, start=1):
                if cls.judgeConstraint(passenger, driver):
                    canDri.append(j)
                    candidateActions.append(M*i + j)
            cadidateTable.append(canDri)
        print('candidateActions:{}'.format(len(candidateActions)))
        return candidateActions, cadidateTable

    @classmethod
    def judgeConstraint(cls, passenger, driver) -> bool:
        # radium constraint for driver
        orgDist = cls.calNodeDist(driver.getOrg(), passenger.getOrg())
        if orgDist > RADIUS:
            return False
        # waitTime constraint for passenger
        if orgDist/SPEED > passenger.getWaitTime():
            return False
        # detour constraint for driver
        sharedDist = orgDist + passenger.iDist + \
            cls.calNodeDist(driver.getDst(), passenger.getDst())
        if sharedDist > (1+driver.getDetourRatio())*driver.iDist:
            return False
        return True


if __name__ == '__main__':
    pass
