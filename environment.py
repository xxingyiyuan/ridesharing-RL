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

        drivers_df = pd.read_table('./requests_300_1.txt', sep=' ', header=None, names=[
                                   'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude'])
        drivers_df['seatNum'] = 5
        drivers_df['detourRatio'] = detourRatio
        passengers_df = pd.read_table('./requests_600_1.txt', sep=' ', header=None, names=[
                                      'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude'])
        passengers_df['seatNum'] = np.array([2,2,2,1,1,1,1,1,2,2,1,2,1,1,2,2,2,2,1,1,2,2,2,2,1,2,2,1,1,2,2,1,1,2,1,2,2,2,2,2,2,1,2,1,2,2,1,2,1,2,2,2,1,1,1,1,1,1,1,2,1,1,2,1,2,2,2,1,1,2,1,2,2,2,2,1,2,1,2,2,2,1,2,2,2,2,2,1,2,1,1,2,2,1,1,1,1,2,1,1,2,2,2,1,2,1,2,2,1,1,2,2,2,2,2,1,1,2,1,1,1,2,1,1,2,1,2,1,1,1,1,2,1,1,2,2,2,1,2,2,1,2,1,2,1,1,1,2,2,1,1,1,2,2,1,2,2,1,2,1,2,1,2,1,1,1,1,1,1,1,1,1,2,1,1,1,1,2,2,2,2,2,1,2,2,2,1,2,2,1,1,1,2,2,2,1,1,2,2,1,1,2,1,1,1,2,2,2,2,2,2,2,2,1,1,2,1,2,2,2,2,1,2,1,2,2,1,2,1,2,1,1,1,1,2,2,2,2,2,2,1,2,2,1,2,1,1,1,2,2,1,1,1,2,2,2,2,2,2,1,2,2,2,1,2,2,1,1,2,2,2,2,1,1,1,2,1,1,1,1,1,1,1,2,1,2,1,2,1,2,2,2,2,2,2,2,2,1,2,1,2,1,1,1,1,1,1,2,1,1,2,2,2,1,1,1,2,2,1,1,2,2,2,2,1,1,2,2,2,1,2,2,2,1,1,1,1,1,2,2,1,1,2,1,2,1,1,1,2,2,2,1,2,1,1,1,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,2,1,2,1,2,1,1,1,1,2,2,2,1,1,2,1,2,1,1,2,1,2,1,1,1,1,2,1,1,2,1,2,2,1,2,2,1,1,2,1,2,2,1,1,2,1,2,1,1,1,1,1,2,1,1,1,2,1,2,2,2,2,1,1,1,2,2,1,2,1,2,1,2,1,1,1,2,2,2,1,1,1,2,2,2,1,1,2,1,2,2,1,1,2,2,2,2,1,2,2,2,1,1,2,1,2,2,1,2,2,1,2,2,2,2,1,1,1,1,1,1,1,1,1,2,1,2,1,2,2,1,2,2,1,2,2,2,1,1,1,2,2,1,2,2,1,2,2,2,2,2,1,1,1,2,1,2,2,2,2,1,1,1,2,2,1,1,2,2,2,1,2,2,2,2,1,1,2,1,2,2,1,1,1,1,2,1,1,2,1,1,2,1,1,1,1,2,2,2,1,1,2,1,1,2,1,2,1,1,1,1,2,2,1,2,2,1,1,1,2,2,2,1,2,1,1,2,2,2])
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
        # self.auctioneer.auction(self.drivers, self.coalitions)
        return self.getObservation()

    def getObservation(self):
        obs = [p.driverId for p in self.passengers]
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
                return (self.getObservation(), -1, False)
            else:
                self.auctioneer.auction(self.drivers, self.coalitions)
                observation_ = self.getObservation()
                reward = self.getPassTotalUtility() - self.passUti
                self.passUti = self.getPassTotalUtility()
                if reward == 0:
                    reward = 100
                
                return (observation_, reward, False)
        # case 2 leave: cur_driverId != 0 and target_driverId == 0, remove passenger from cur_driverId
        elif cur_driverId != 0 and target_driverId == 0:
            cur_coalition.removePassenger(passenger)
            self.auctioneer.auction(self.drivers, self.coalitions)
            observation_ = self.getObservation()
            reward = self.getPassTotalUtility() - self.passUti
            self.passUti = self.getPassTotalUtility()
            return (observation_, reward, False)
        # case 3 switch: cur_driverId != 0 and target_driverId != 0, remove passenger from cur_driverId and add passenger to target_driverId
        else:
            cur_coalition.removePassenger(passenger)
            flag = target_coalition.addPassenger(passenger)
            self.auctioneer.auction(self.drivers, self.coalitions)
            observation_ = self.getObservation()
            reward = self.getPassTotalUtility() - self.passUti
            self.passUti = self.getPassTotalUtility()
            return (observation_, reward, False)

      

    def initAssignment(self):
        matching = [[44, 73, 94, 146], [205], [182], [551], [362, 596], [12, 32], [93], [192, 386], [119, 148, 394], [481], [0], [98, 135, 538], [25, 250], [6, 296], [16], [153], [187], [586], [0], [562], [27, 274, 315], [300], [0], [64, 85, 400], [407], [454], [246, 531], [143, 306, 323], [107, 558], [2, 48, 443], [8, 176, 543, 553], [430], [10, 82, 101], [288, 392], [336], [0], [99, 368, 487], [164], [75, 217], [0], [0], [134, 509], [0], [239, 401], [351], [103, 109, 415], [0], [22, 79, 145], [14], [127, 201], [467], [140], [0], [468], [185], [90, 224], [199, 223], [29], [45, 387, 527], [0], [211], [0], [151, 163], [50, 520], [0], [462], [363], [0], [338, 482], [0], [0], [116], [326], [599], [275, 552], [194, 264, 374], [55, 208, 261], [0], [345, 472], [0], [501], [230], [0], [0], [0], [396], [168, 235, 441], [9, 51, 175], [183], [354, 554], [293], [343, 380, 413], [258], [245, 337, 423], [49, 234, 450], [28, 154, 594], [0], [303, 564], [0], [0], [203, 381], [33, 123, 124, 314], [373], [0], [72, 212, 575], [11, 104, 395, 479], [0], [62, 142, 352], [31, 42], [444], [169, 474, 503], [133, 328], [102, 196, 197, 310], [389], [0], [580], [318, 397], [0], [0], [243, 279, 366], [581], [43, 66], [557], [76, 78, 80, 170], [92, 184, 302], [129, 237], [416], [188, 312], [0], [0], [0], [0], [0], [0], [414, 571, 574], [0], [0], [18, 391, 399], [5, 206], [0], [207, 324], [178], [202, 402, 461], [232], [
            0], [162, 370], [61], [0], [229, 238], [495], [253], [0], [0], [0], [180, 236, 377], [533], [56], [13, 372], [0], [36, 273, 537], [34], [108, 147, 241], [0], [305], [438], [498], [452], [0], [95], [21, 26, 567], [30, 244, 333], [0], [156], [193, 287], [547, 583], [0], [267, 522], [172, 584], [0], [0], [0], [128], [15, 437], [0], [111, 349], [115], [0], [157], [284, 518], [0], [117, 252, 582], [68, 257, 405], [0], [404, 480], [214, 500], [174, 475], [292, 504], [190], [355, 530, 535], [0], [52, 529], [334, 466], [266], [465], [448], [263, 335, 382], [0], [0], [0], [0], [0], [270, 286, 514], [0], [189, 231], [53], [0], [435], [442], [20, 87, 560], [141, 330], [0], [210], [67, 70, 106], [319, 375], [218, 249], [0], [0], [17], [200], [329], [57, 325, 327], [322], [0], [365, 459, 579], [7, 598], [0], [59], [114], [81, 295], [195], [0], [213, 320, 440], [0], [490], [69, 136, 220], [0], [41, 160, 417], [222, 570], [35, 297, 342], [0], [549], [39, 65], [1], [0], [0], [131, 546, 588], [227, 508], [161, 260], [209, 221, 532], [390], [0], [0], [344], [281], [0], [38], [411, 473, 521], [341], [225, 451], [0], [0], [138, 150, 422], [19], [565], [139], [0], [247, 271], [429, 572], [4, 100], [37, 177], [511], [494], [311, 358], [152], [251], [432, 516], [126, 433], [346], [280], [125], [159, 317], [58, 171, 228], [88, 186, 216], [409, 492, 576], [97], [130, 493], [348, 439], [3], [24, 40], [536]]
        for driverId, passList in enumerate(matching, start=1):
            coalition = self.coalitions[driverId]
            for passId in passList:
                if passId == 0:
                    break
                passenger = self.passengers[passId-1]
                coalition.addPassenger(passenger)


if __name__ == '__main__':

    Env = Environment(drivers_num=300, passengers_num=600, waitTime=2)
