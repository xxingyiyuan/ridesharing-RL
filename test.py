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
from demand import Demand

# 取消科学计数法
np.set_printoptions(suppress=True)


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


# def test(datasetSettings, waitTime, detourRatio):
#     generator = Generator(*datasetSettings)
#     drivers_demand, passengers_demand = initDemands(
#         generator, waitTime, detourRatio)
#     res = np.zeros((4, 5))
#     res[0] = carpool(1, drivers_demand, passengers_demand)
#     res[1] = carpool(2, drivers_demand, passengers_demand)
#     res[2] = carpool(3, drivers_demand, passengers_demand)
#     res[3] = carpool(4, drivers_demand, passengers_demand)
#     print(res)


if __name__ == '__main__':
    demandInstance = Demand()
    dataset = {
        'beijing': settings.beijingRange,
        'guangzhou': settings.guangzhouRange,
        'newyork': settings.newyorkRange
    }
    datasetName = 'newyork'

    defaultWaitTime = 4
    defaultDetourRatio = 0.4

    fileNums = [i for i in range(5)]
    drivers_num = 40
    passengers_num = 80
    # 生成请求
    # generateFiles(datasetName, dataset[datasetName],
    #               fileNums, drivers_num, passengers_num)

    

 
