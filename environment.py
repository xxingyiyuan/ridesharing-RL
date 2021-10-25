import re

from numpy.core.fromnumeric import put
from generalRequest import Generator
import random
import pandas as pd
import numpy as np
import settings
from driver import Driver
from passenger import Passenger
from coalition import Coalition
from auctioneer import Auctioneer
from tool import Tool
# dataset
G = Generator(*settings.beijingRange)


class Environment:
    def __init__(self, drivers_num, passengers_num, waitTime=5, detourRatio=0.5):
        self.drivers_num = drivers_num
        self.passengers_num = passengers_num
        self.M = drivers_num + 1
        self.N = passengers_num
        self.auctioneer = Auctioneer()
        self.initDemands(waitTime, detourRatio)
        self.initParticipants()
        self.candidateActions, self.candidateTable = Tool.getCandidateActions(
            self.drivers, self.passengers)
        self.passUti = 0

    def initDemands(self, waitTime, detourRatio):
        # initialize demands
        # pickup_longitude  pickup_latitude  dropoff_longitude  dropoff_latitude  seatNum detourRatio waitTime

        # self.seed = 1
        # random.seed(self.seed)
        # np.random.seed(self.seed)

        # total_num, isRandom, detourRatio, waitTime=None
        
        # self.drivers_demand = G.generateRequests(
        #     total_num=self.drivers_num, isRandom=False, detourRatio=detourRatio, waitTime=None)
        # self.passengers_demand = G.generateRequests(
        #     total_num=self.passengers_num, isRandom=True, detourRatio=detourRatio, waitTime=waitTime)

        drivers_df = pd.read_table('./requests_50_1.txt', sep=' ', header=None, names=[
                                   'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude'])
        drivers_df['seatNum'] = 5
        drivers_df['detourRatio'] = detourRatio
        passengers_df = pd.read_table('./requests_100_1.txt', sep=' ', header=None, names=[
                                      'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude'])
        passengers_df['seatNum'] = 1
        passengers_df['detourRatio'] = detourRatio
        passengers_df['waitTime'] = waitTime
        self.drivers_demand = drivers_df
        self.passengers_demand = passengers_df

    def initParticipants(self):
        drivers_demand = [tuple(de)
                          for de in self.drivers_demand.values]
        self.drivers = [Driver(id, de)
                        for id, de in enumerate(drivers_demand, start=1)]
        # print(self.drivers[0])
        passengers_demand = [tuple(de)
                             for de in self.passengers_demand.values]
        self.passengers = [Passenger(id, de)
                           for id, de in enumerate(passengers_demand, start=1)]

        # print(self.passengers[0])

    def resetEnv(self):
        # initialize drivers and passengers
        self.initParticipants()
        # initialize coalitions
        self.coalitions = {}
        for d in self.drivers:
            self.coalitions[d.id] = Coalition(d)
        # self.initAssignment()
        return self.getObservation(), self.getPassTotalUtility()

    def initAssignment(self):
        for passIndex, canDri in enumerate(self.candidateTable):
            for driverId in canDri:
                coalition = self.coalitions[driverId]
                if coalition.addPassenger(self.passengers[passIndex]):
                    break
        self.auctioneer.auction(self.drivers, self.coalitions)

    def getObservation(self):
        obs = [p.driverId for p in self.passengers]
        # obs = [d.sPassengerNum for d in self.drivers]
        return np.array(obs)

    def getPassTotalUtility(self):
        pUti = [p.getUtility() for p in self.passengers]
        return sum(pUti)

    def step(self, action) -> tuple:
        # return: (observation_, reward, done)
        passengerIndex = int(action/self.M)
        passenger = self.passengers[passengerIndex]
        target_driverId = int(action % self.M)
        cur_driverId = passenger.driverId
        # no execution
        if cur_driverId == target_driverId:
            return (self.getObservation(), 0, False)
        # get coalition
        if cur_driverId:
            cur_coalition = self.coalitions[cur_driverId]
        if target_driverId:
            target_coalition = self.coalitions[target_driverId]
        # case 1 join: cur_driverId == 0 and target_driverId != 0 add passenger to target_driverId
        if cur_driverId == 0 and target_driverId != 0:
            flag = target_coalition.addPassenger(passenger)
            # break constraints
            if flag == False:
                reward = -1000
                return (self.getObservation(), reward, False)
            else:
                # join
                self.auctioneer.auction(self.drivers, self.coalitions)
                observation_ = self.getObservation()
                reward = (self.getPassTotalUtility() - self.passUti)*10
                self.passUti = self.getPassTotalUtility()
                return (observation_, reward, False)
        # case 2 leave: cur_driverId != 0 and target_driverId == 0, remove passenger from cur_driverId
        elif cur_driverId != 0 and target_driverId == 0:
            cur_coalition.removePassenger(passenger)
            self.auctioneer.auction(self.drivers, self.coalitions)
            observation_ = self.getObservation()
            reward = (self.getPassTotalUtility() - self.passUti)*10
            self.passUti = self.getPassTotalUtility()
            return (observation_, reward, False)
        # case 3 switch: cur_driverId != 0 and target_driverId != 0, remove passenger from cur_driverId and add passenger to target_driverId
        else:
            cur_coalition.removePassenger(passenger)
            flag = target_coalition.addPassenger(passenger)
            self.auctioneer.auction(self.drivers, self.coalitions)
            observation_ = self.getObservation()
            reward = (self.getPassTotalUtility() - self.passUti)*10
            self.passUti = self.getPassTotalUtility()
            return (observation_, reward, False)


if __name__ == '__main__':

    Env = Environment(drivers_num=50, passengers_num=100, waitTime=2)
