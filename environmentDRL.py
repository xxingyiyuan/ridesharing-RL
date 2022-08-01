import numpy as np
from driver import Driver
from passenger import Passenger
from coalition import Coalition
from auctioneer import Auctioneer
from tool import Tool


class Environment:
    def __init__(self, drivers_demand, passengers_demand):
        self.M = len(drivers_demand) + 1
        self.N = len(passengers_demand)
        self.drivers_demand = drivers_demand
        self.passengers_demand = passengers_demand
        self.initParticipants()
        self.candidateActions, self.candidateTable = Tool.getCandidateActions(
            self.drivers, self.passengers)
        # 这个是所有动作的索引
        self.candidateIndex = [i for i in range(len(self.candidateActions))]
        # 动作编码和动作索引的映射
        self.actionMap = {}
        for (i, action) in enumerate(self.candidateActions):
            self.actionMap[action] = i
        self.passUti = self.getPassTotalUtility()
        # 初始状态
        self.passWindow = np.zeros(self.N)

    def initParticipants(self):
        self.drivers = [Driver(id, de)
                        for id, de in enumerate(self.drivers_demand, start=1)]
        self.passengers = [Passenger(id, de) for id, de in enumerate(
            self.passengers_demand, start=1)]
        # initialize coalition
        self.coalitions = {}
        for d in self.drivers:
            self.coalitions[d.id] = Coalition(d)
        self.auctioneer = Auctioneer(self.drivers, self.coalitions)

    def resetEnv(self):
        # reset drivers and passengers
        self.initParticipants()
        self.passWindow = np.zeros(self.N)
        self.candidateIndex = [i for i in range(len(self.candidateActions))]
        self.passUti = self.getPassTotalUtility()
        return self.getObservation(), self.getPassTotalUtility()

    def getObservation(self):
        return self.passWindow

    def getPassTotalUtility(self):
        pUti = [p.getUtility() for p in self.passengers]
        return sum(pUti)

    def getVaildIndex(self):
        # the index of assigned passengers
        invalidPassIndex = np.where(self.passWindow != 0)[0]
        invalidAction = [passIndex*self.M for passIndex in invalidPassIndex]
        for passIndex in invalidPassIndex:
            for driverId in self.candidateTable[passIndex]:
                action = passIndex*self.M + driverId
                invalidAction.append(action)
        invalidAction = list(set(invalidAction))
        candidateIndex = []
        for i, action in enumerate(self.candidateActions):
            if action in invalidAction:
                continue
            candidateIndex.append(i)
        return candidateIndex

    def step(self, action) -> tuple:
        # return: (observation_, reward, done)
        passengerIndex = int(action/self.M)
        passenger = self.passengers[passengerIndex]
        target_driverId = int(action % self.M)
        # no execution cur_driverId = target_driverId = 0
        if target_driverId == 0:
            reward = 0
            self.passWindow[passengerIndex] = 1
        else:
            # join: cur_driverId == 0 and target_driverId != 0 add passenger to target_driverId
            target_coalition = self.coalitions[target_driverId]
            flag = target_coalition.addPassenger(passenger)
            # break constraints
            if flag == False:
                reward = -50
                # self.passWindow[passengerIndex] = 1
                return (self.getObservation(), reward, 2)
            else:
                # join
                self.auctioneer.auction()
                reward = (self.getPassTotalUtility() - self.passUti)
                self.passUti = self.getPassTotalUtility()
                self.passWindow[passengerIndex] = 1
        if self.passWindow[passengerIndex] == 1:
            # 移除跟当前乘客的相关action
            self.updateValidIndex(passengerIndex)
        done = 0 not in self.passWindow
        observation_ = self.getObservation()
        return (observation_, reward, done)

    def updateValidIndex(self, passIndex):
        # 无效的action
        invalidAction = [passIndex*self.M]
        for driverId in self.candidateTable[passIndex]:
            invalidAction.append(passIndex*self.M + driverId)
        for action in invalidAction:
            actionIndex = self.actionMap[action]
            if actionIndex in self.candidateIndex:
                self.candidateIndex.remove(actionIndex)
