from generalRequest import Generator
import pandas as pd
import numpy as np
import settings
import random
from driver import Driver
from passenger import Passenger
from tool import Tool
from algorithmCFA import AlgorithmCFA
from algorithmTSG import AlgorithmTSG
from algorithmOTMBM import AlgorithmOTMBM
from algorithmDRL import AlgorithmDRL
from algorithmDiDi import AlgorithmDiDi
from demand import Demand

# 取消科学计数法
np.set_printoptions(suppress=True)


def initDemands(generator: Generator, waitTime, detourRatio, drivers_num=40, passengers_num=80):
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
    # --------------- generate demands --------------
    # -----------------------------------------------
    drivers_df = generator.generateRequests(total_num=drivers_num, flag=0)
    passengers_df = generator.generateRequests(
        total_num=passengers_num, flag=1)

    # add detour and waitTime
    drivers_df['detourRatio'] = random.uniform(
        detourRatio, detourRatio + 0.1)
    passengers_df['detourRatio'] = random.uniform(
        detourRatio, detourRatio + 0.1)
    passengers_df['waitTime'] = random.uniform(waitTime, waitTime + 1)
    drivers_demand = [tuple(de) for de in drivers_df.values]
    passengers_demand = [tuple(de) for de in passengers_df.values]
    return drivers_demand, passengers_demand


def initParticipants(drivers_demand, passengers_demand, isVocational=False):
    drivers = [Driver(id, de, isVocational)
               for id, de in enumerate(drivers_demand, start=1)]
    passengers = [Passenger(id, de)
                  for id, de in enumerate(passengers_demand, start=1)]
    dcaMat, pcaMat = Tool.getCandidates(drivers, passengers)
    return drivers, dcaMat, passengers, pcaMat


def carpool(select, drivers_demand, passengers_demand):
    if select == 1:
        drivers, dcaMat, passengers, pcaMat = initParticipants(
            drivers_demand, passengers_demand)
        CFA = AlgorithmCFA(drivers, dcaMat, passengers, pcaMat)
        return CFA.collectData()
    elif select == 2:
        drivers, dcaMat, passengers, pcaMat = initParticipants(
            drivers_demand, passengers_demand)
        TSG = AlgorithmTSG(drivers, dcaMat, passengers, pcaMat)
        return TSG.collectData()
    elif select == 3:
        drivers, dcaMat, passengers, pcaMat = initParticipants(
            drivers_demand, passengers_demand)
        OTMBM = AlgorithmOTMBM(drivers, dcaMat, passengers, pcaMat)
        return OTMBM.collectData()
    elif select == 4:
        DRL = AlgorithmDRL(drivers_demand, passengers_demand)
        return DRL.collectData()
    elif select == 5:
        drivers, dcaMat, passengers, pcaMat = initParticipants(
            drivers_demand, passengers_demand, isVocational=True)
        DiDi = AlgorithmDiDi(drivers, dcaMat, passengers, pcaMat)
        return DiDi.collectData()


def getPartition(leftbottom, regionShape, squreSize):
    initX, initY = leftbottom
    leftbottoms = []
    for i in range(2):
        y = initY + i*regionShape[1]*squreSize[1]
        for j in range(2):
            x = initX + j*regionShape[0]*squreSize[0]
            leftbottoms.append((x, y))
    return leftbottoms


def generateFiles(datasetName, datasetSettings, fileNums=[0], drivers_num=40, passengers_num=80):
    # 生成request文件
    filepath, leftbottom, regionShape, squreSize = datasetSettings
    # leftbottoms = getPartition(leftbottom, regionShape, squreSize)
    for i in fileNums:
        # leftbottom = random.choice(leftbottoms)
        generator = Generator(filepath, leftbottom, regionShape, squreSize)
        drivers_df = generator.generateRequests(total_num=drivers_num, flag=0)
        passengers_df = generator.generateRequests(
            total_num=passengers_num, flag=1)
        drivers_df.to_csv('./data/{}/driver_requests/driver_requests_{}_{}.txt'.format(
            datasetName, drivers_num, i), sep=' ', header=None, index=False)
        passengers_df.to_csv('./data/{}/passenger_requests/passenger_requests_{}_{}.txt'
                             .format(datasetName, passengers_num, i), sep=' ', header=None, index=False)


def loadDemand(datasetName, fileNum, waitTime, detourRatio, drivers_num=40, passengers_num=80):
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


def collectData(datasetName, fileNum, waitTime, detourRatio, drivers_num, passengers_num):
    drivers_demand, passengers_demand = loadDemand(
        datasetName, fileNum, waitTime, detourRatio, drivers_num, passengers_num)
    res = np.zeros((4, 5))
    res[0] = carpool(1, drivers_demand, passengers_demand)
    res[1] = carpool(2, drivers_demand, passengers_demand)
    res[2] = carpool(3, drivers_demand, passengers_demand)
    res[3] = carpool(4, drivers_demand, passengers_demand)
    # print(res)
    return res


def test(datasetSettings, waitTime, detourRatio):
    generator = Generator(*datasetSettings)
    drivers_demand, passengers_demand = initDemands(
        generator, waitTime, detourRatio, 300, 600)
    res = np.zeros((4, 5))
    res[0] = carpool(1, drivers_demand, passengers_demand)
    res[1] = carpool(2, drivers_demand, passengers_demand)
    res[2] = carpool(3, drivers_demand, passengers_demand)
    res[3] = carpool(5, drivers_demand, passengers_demand)
    # print(res)
    return res


if __name__ == '__main__':
    demandInstance = Demand()
    dataset = {
        'beijing': settings.beijingRange,
        'guangzhou': settings.guangzhouRange,
        'newyork': settings.newyorkRange
    }
    datasetName = 'beijing'

    defaultWaitTime = 5
    defaultDetourRatio = 0.5
    res = np.zeros((4, 5))
    for i in range(1):
        res += test(dataset[datasetName], defaultWaitTime, defaultDetourRatio)

    # 将numpy数组转换为pandas数据帧
    df = pd.DataFrame(res)
    df.insert(0, 'algorithm', ['CFA', 'TSG', 'OTMBM', 'DiDi'])
    print(df)
    # 将数据帧保存为Excel文件
    df.to_csv('./result/didi.csv', index=False, header=['algorithm', 'passenger utility',
              'passenger number', 'driver utility', 'driver number', ' running time'])

    # fileNums = [i for i in range(5)]
    # drivers_num = 40
    # passengers_num = 80
    # 生成请求
    # generateFiles(datasetName, dataset[datasetName],
    #               fileNums, drivers_num, passengers_num)

    # waitTime = defaultWaitTime
    # for detourRatio in [0.2, 0.3, 0.4, 0.5, 0.6]:
    #     res = np.zeros((4, 5))
    #     for file_num in fileNums:
    #         tmp = collectData(datasetName, file_num, waitTime,
    #                           detourRatio, drivers_num, passengers_num)
    #         np.savetxt('./result/{}/detourRatio/file{}-waitTime={}-detourRatio={}.csv'.format(
    #             datasetName, file_num, waitTime, detourRatio), tmp, delimiter=',', fmt='%.3f')
    #         res += tmp
    #     # total result
    #     np.savetxt('./result/{}/detourRatio/total-waitTime={}-detourRatio={}.csv'.format(
    #         datasetName, waitTime, detourRatio), res, delimiter=',', fmt='%.3f')

    # detourRatio = defaultDetourRatio
    # for waitTime in range(2, 3):
    #     res = np.zeros((4, 5))
    #     for file_num in fileNums:
    #         tmp = collectData(datasetName, file_num, waitTime,
    #                           detourRatio, drivers_num, passengers_num)
    #         np.savetxt('./result/{}/waitTime/file{}-waitTime={}-detourRatio={}.csv'.format(
    #             datasetName, file_num, waitTime, detourRatio), tmp, delimiter=',', fmt='%.3f')
    #         res += tmp
    #     # total result
    #     np.savetxt('./result/{}/waitTime/total-waitTime={}-detourRatio={}.csv'.format(
    #         datasetName, waitTime, detourRatio), res, delimiter=',', fmt='%.3f')
