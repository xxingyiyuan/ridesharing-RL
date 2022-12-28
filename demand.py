import pandas as pd
import random
from driver import Driver
from passenger import Passenger
from tool import Tool


class Demand:
    # @classmethod
    # def initDemands(cls, generator: Generator, waitTime, detourRatio, drivers_num=40, passengers_num=80):
    #     """initialize demands

    #     Args:
    #         waitTime (int): passenger tolerable waiting time
    #         detourRatio (float): driver/passenger tolerable detour ratio
    #         drivers_num (int, optional): _description_. Defaults to 50.
    #         passengers_num (int, optional): _description_. Defaults to 100.
    #         file_num (int, optional): use to store/read data file. Defaults to 0.
    #         isSave (boolean, optional): save the file or not
    #     Returns:
    #         _type_: drivers_df, passengers_df
    #     """
    #     st0 = np.random.get_state()
    #     seed = np.random.set_state(st0)
    #     random.seed(seed)
    #     np.random.seed(seed)
    #     # -----------------------------------------------
    #     # --------------- generate demands --------------
    #     # -----------------------------------------------
    #     drivers_df = generator.generateRequests(total_num=drivers_num, flag=0)
    #     passengers_df = generator.generateRequests(
    #         total_num=passengers_num, flag=1)

    #     # add detour and waitTime
    #     drivers_df['detourRatio'] = random.uniform(
    #         detourRatio, detourRatio + 0.1)
    #     passengers_df['detourRatio'] = random.uniform(
    #         detourRatio, detourRatio + 0.1)
    #     passengers_df['waitTime'] = random.uniform(waitTime, waitTime + 1)
    #     drivers_demand = [tuple(de) for de in drivers_df.values]
    #     passengers_demand = [tuple(de) for de in passengers_df.values]
    #     return drivers_demand, passengers_demand

    @classmethod
    def initParticipants(cls, drivers_demand, passengers_demand):
        drivers = [Driver(id, de)
                   for id, de in enumerate(drivers_demand, start=1)]
        passengers = [Passenger(id, de)
                      for id, de in enumerate(passengers_demand, start=1)]
        dcaMat, pcaMat = Tool.getCandidates(drivers, passengers)
        return drivers, dcaMat, passengers, pcaMat

    @classmethod
    def generateFiles(cls, datasetName, datasetSettings, fileNums=[0], drivers_num=40, passengers_num=80):
        # 生成request文件
        filepath, leftbottom, regionShape, squreSize = datasetSettings
        # leftbottoms = getPartition(leftbottom, regionShape, squreSize)
        for i in fileNums:
            # leftbottom = random.choice(leftbottoms)
            generator = Generator(filepath, leftbottom, regionShape, squreSize)
            drivers_df = generator.generateRequests(
                total_num=drivers_num, flag=0)
            passengers_df = generator.generateRequests(
                total_num=passengers_num, flag=1)
            drivers_df.to_csv('./data/{}/driver_requests/driver_requests_{}_{}.txt'.format(
                datasetName, drivers_num, i), sep=' ', header=None, index=False)
            passengers_df.to_csv('./data/{}/passenger_requests/passenger_requests_{}_{}.txt'
                                 .format(datasetName, passengers_num, i), sep=' ', header=None, index=False)

    @classmethod
    def loadDemand(cls, datasetName, fileNum, waitTime, detourRatio, drivers_num=40, passengers_num=80):
        drivers_df = pd.read_table('./data/{}/driver_requests/driver_requests_{}_{}.txt'.format(datasetName, drivers_num, fileNum),
                                   sep=' ', header=None, names=['pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude', 'seatNum'])
        passengers_df = pd.read_table('./data/{}/passenger_requests/passenger_requests_{}_{}.txt'.format(datasetName, passengers_num, fileNum),
                                      sep=' ', header=None, names=['pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude', 'seatNum'])
        # add detour and waitTime
        drivers_df['detourRatio'] = random.uniform(
            detourRatio, detourRatio + 0.1)
        passengers_df['detourRatio'] = random.uniform(
            detourRatio, detourRatio + 0.1)
        passengers_df['waitTime'] = random.uniform(waitTime, waitTime + 1)
        drivers_demand = [tuple(de) for de in drivers_df.values]
        passengers_demand = [tuple(de) for de in passengers_df.values]
        return drivers_demand, passengers_demand
