from generalRequest import Generator
import pandas as pd
import numpy as np
import settings
import random
from driver import Driver
from passenger import Passenger
from tool import Tool
from algorithmCFA import AlgorithmCFA
# dataset
G = Generator(*settings.newyorkRange)


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


def initParticipants(waitTime=4, detourRatio=0.5, drivers_num=40, passengers_num=80):
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
        waitTime, detourRatio, drivers_num, passengers_num, file_num=6)
    drivers_demand = [tuple(de) for de in drivers_df.values]
    drivers = [Driver(id, de) for id, de in enumerate(drivers_demand, start=1)]

    passengers_demand = [tuple(de) for de in passengers_df.values]
    passengers = [Passenger(id, de)
                  for id, de in enumerate(passengers_demand, start=1)]
    return drivers, passengers


def carpool(select):
    drivers, passengers = initParticipants()
    dcaMat, pcaMat = Tool.getCandidates(drivers, passengers)
    if select == 1:
        AlgorithmCFA(drivers, dcaMat, passengers, pcaMat)


if __name__ == '__main__':
    carpool(1)
