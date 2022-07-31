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

    return drivers_df, passengers_df


def initParticipants(waitTime=4, detourRatio=0.5, drivers_num=50, passengers_num=100):
    """_summary_

    Args:
        waitTime (int, optional): _description_. Defaults to 4.
        detourRatio (float, optional): _description_. Defaults to 0.5.
        drivers_num (int, optional): _description_. Defaults to 50.
        passengers_num (int, optional): _description_. Defaults to 100.

    Returns:
        _type_: _description_
    """
    drivers_df, passengers_df = initDemands(
        waitTime, detourRatio, drivers_num, passengers_num, file_num=0)
    drivers_demand = [tuple(de) for de in drivers_df.values]
    drivers = [Driver(id, de) for id, de in enumerate(drivers_demand, start=1)]

    passengers_demand = [tuple(de) for de in passengers_df.values]
    passengers = [Passenger(id, de)
                  for id, de in enumerate(passengers_demand, start=1)]
    return drivers, passengers


def carpool(select, drivers, passengers):
    dcaMat, pcaMat = Tool.getCandidates(drivers, passengers)
    if select == 1:
        CFA = AlgorithmCFA(drivers, dcaMat, passengers, pcaMat)
        return CFA.getTotalUtility()
    elif select == 2:
        TSG = AlgorithmTSG(drivers, dcaMat, passengers, pcaMat)
        return TSG.getTotalUtility()
    elif select == 3:
        OTMBM = AlgorithmOTMBM(drivers, dcaMat, passengers, pcaMat)
        return OTMBM.getTotalUtility()


if __name__ == '__main__':
    res1, res2, res3 = 0, 0, 0
    total = 1
    for _ in range(total):
        for _ in range(1):
            drivers, passengers = initParticipants(
                waitTime=4, detourRatio=0.5, drivers_num=300, passengers_num=600)
            res1 += carpool(1, copy.deepcopy(drivers),
                            copy.deepcopy(passengers))
            res2 += carpool(2, copy.deepcopy(drivers),
                            copy.deepcopy(passengers))
            res3 += carpool(3, copy.deepcopy(drivers),
                            copy.deepcopy(passengers))
    res1 = res1 / total
    res2 = res2 / total
    res3 = res3 / total
    print('alogrithm CFA: ', res1)
    print('alogrithm TSG: ', res2, (res1 / res2 - 1) * 100)
    print('alogrithm OTMBM: ', res3, (res1 / res3 - 1) * 100)
