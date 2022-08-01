from generalRequest import Generator
import pandas as pd
import numpy as np
import settings
import random
import copy
from driver import Driver
from passenger import Passenger
from tool import Tool
from algorithmCFA import AlgorithmCFA
from algorithmTSG import AlgorithmTSG
from algorithmOTMBM import AlgorithmOTMBM
from algorithmDRL import AlgorithmDRL
# dataset
G = Generator(*settings.beijingRange)


def initDemands(waitTime, detourRatio, drivers_num, passengers_num, file_num=0, isSave=False):
    """initialize demands

    Args:
        waitTime (int): passenger tolerable waiting time
        detourRatio (float): driver/passenger tolerable detour ratio
        drivers_num (int, optional): _description_. Defaults to 50.
        passengers_num (int, optional): _description_. Defaults to 100.
        file_num (int, optional): use to store/read data file. Defaults to 0.
        isSave (boolean, optional): save the file or not 
    Returns:
        _type_: drivers_df, passengers_df
    """

    st0 = np.random.get_state()
    seed = np.random.set_state(st0)
    random.seed(seed)
    np.random.seed(seed)

    # -----------------------------------------------
    # ---------------- read demands ----------------
    # -----------------------------------------------
    if file_num:
        drivers_df = pd.read_table('./data/driver_requests/driver_requests_{}_{}.txt'.format(drivers_num, file_num), sep=' ',
                                   header=None, names=['pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude', 'seatNum'])
        passengers_df = pd.read_table('./data/passenger_requests/passenger_requests_{}_{}.txt'.format(passengers_num, file_num), sep=' ',
                                      header=None, names=['pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude', 'seatNum'])
    else:
        # -----------------------------------------------
        # --------------- generate demands --------------
        # -----------------------------------------------
        drivers_df = G.generateRequests(total_num=drivers_num, flag=0)
        passengers_df = G.generateRequests(total_num=passengers_num, flag=1)

    # -----------------------------------------------
    # ---------------- store demands ----------------
    # -----------------------------------------------
    if isSave:
        drivers_df.to_csv('./data/driver_requests/driver_requests_{}_{}.txt'.format(
            drivers_num, file_num), sep=' ', header=None, index=False)
        passengers_df.to_csv('./data/passenger_requests/passenger_requests_{}_{}.txt'.format(
            passengers_num, file_num), sep=' ', header=None, index=False)
    # add detour and waitTime
    drivers_df['detourRatio'] = detourRatio
    passengers_df['detourRatio'] = detourRatio
    passengers_df['waitTime'] = waitTime

    drivers_demand = [tuple(de) for de in drivers_df.values]
    passengers_demand = [tuple(de) for de in passengers_df.values]
    return drivers_demand, passengers_demand


def initParticipants(drivers_demand, passengers_demand):
    drivers = [Driver(id, de) for id, de in enumerate(drivers_demand, start=1)]
    passengers = [Passenger(id, de)
                  for id, de in enumerate(passengers_demand, start=1)]
    dcaMat, pcaMat = Tool.getCandidates(drivers, passengers)
    return drivers, dcaMat, passengers, pcaMat


def carpool(select, drivers_demand, passengers_demand):

    if select == 1:
        drivers, dcaMat, passengers, pcaMat = initParticipants(
            drivers_demand, passengers_demand)
        CFA = AlgorithmCFA(drivers, dcaMat, passengers, pcaMat)
        return CFA.getTotalUtility()
    elif select == 2:
        drivers, dcaMat, passengers, pcaMat = initParticipants(
            drivers_demand, passengers_demand)
        TSG = AlgorithmTSG(drivers, dcaMat, passengers, pcaMat)
        return TSG.getTotalUtility()
    elif select == 3:
        drivers, dcaMat, passengers, pcaMat = initParticipants(
            drivers_demand, passengers_demand)
        OTMBM = AlgorithmOTMBM(drivers, dcaMat, passengers, pcaMat)
        return OTMBM.getTotalUtility()
    elif select == 4:
        DRL = AlgorithmDRL(drivers_demand, passengers_demand)
        return DRL.getTotalUtility()


if __name__ == '__main__':
    total = 10
    res = np.zeros((total, 4))
    for i in range(total):
        for _ in range(6):
            drivers_demand, passengers_demand = initDemands(
                waitTime=4, detourRatio=0.5, drivers_num=50, passengers_num=100)
            res[i][0] += carpool(1, drivers_demand, passengers_demand)
            res[i][1] += carpool(2, drivers_demand, passengers_demand)
            res[i][2] += carpool(3, drivers_demand, passengers_demand)
            res[i][3] += carpool(4, drivers_demand, passengers_demand)
        print(res[i])

    # avg = np.sum(res, axis=0) / total
    avg = np.sum(res, axis=0)
    print(avg)
    print('algorithm CFA: ', avg[0] / avg[1], avg[0] / avg[2])
    print('algorithm DRL: ', avg[3] / avg[1], avg[3] / avg[2])
