import numpy as np
import pandas as pd
import math


class Generator:

    def __init__(self, filepath, leftbottom, regionShape, squreSize):
        self.ROW_NUM = regionShape[0]
        self.COL_NUM = regionShape[1]

        self.REGION_WIDTH = squreSize[0]
        self.REGION_HEIGHT = squreSize[1]

        self.minX = leftbottom[0]
        self.minY = leftbottom[1]
        self.maxX = self.minX + self.COL_NUM*self.REGION_WIDTH
        self.maxY = self.minY + self.ROW_NUM*self.REGION_HEIGHT

        self.probability_df = None
        self.pickup_counts = None

        df = pd.read_table(filepath, sep=',', header=None, names=[
                           'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude'])
        # 获取经纬度范围内的数据
        df = df[(df['pickup_longitude'] > self.minX) &
                (df['pickup_longitude'] < self.maxX)]
        df = df[(df['dropoff_longitude'] > self.minX) &
                (df['dropoff_longitude'] < self.maxX)]
        df = df[(df['pickup_latitude'] > self.minY) &
                (df['pickup_latitude'] < self.maxY)]
        df = df[(df['dropoff_latitude'] > self.minY) &
                (df['dropoff_latitude'] < self.maxY)]
        # 过滤距离较近的数据
        dist = np.power(df['pickup_longitude'] - df['dropoff_longitude'], 2) + \
            np.power(df['pickup_latitude'] -
                     df['dropoff_latitude'], 2)
        df1 = df[dist > 0.0007].copy()
        self.computeProbability(df1)

    # 返回请求所在区域id（0~120）
    def getRegionNum(self, location):
        longitude, latitude = location
        weight = longitude - self.minX
        height = latitude - self.minY
        col_index = math.floor(weight / self.REGION_WIDTH)
        row_index = math.floor(height / self.REGION_HEIGHT)
        region_num = row_index*self.COL_NUM + col_index
        return region_num

    # 增加两列 pickup_region, dropoff_region,分别表示起点所在区域和终点所在区域
    def add_region(self, df):
        pickup_df = df[['pickup_longitude', 'pickup_latitude']]
        pickup_region = pickup_df.apply(self.getRegionNum, axis=1)
        dropoff_df = df[['dropoff_longitude', 'dropoff_latitude']]
        dropoff_region = dropoff_df.apply(self.getRegionNum, axis=1)
        df['pickup_region'] = pickup_region
        df['dropoff_region'] = dropoff_region

    # 生成请求终点所在的区域
    def getDestRegionId(self, origin_rid):
        # 不要用probability_df[origin_rid]
        probability_regions = self.probability_df.loc[origin_rid]
        regions = probability_regions[probability_regions > 0].cumsum()
        id_regions = regions.index
        alpha = np.random.random()
        for (i, v) in enumerate(regions.values):
            if(v >= alpha):
                dest_rid = id_regions[i]
                break
        return dest_rid

    # 获取区域范围
    def getRegionRange(self, region_id):
        row_idx = math.floor(region_id / self.COL_NUM)
        col_idx = region_id % self.COL_NUM
        min_long = self.minX + col_idx * self.REGION_WIDTH
        max_long = self.minX + (col_idx+1) * self.REGION_WIDTH
        min_lat = self.minY + row_idx * self.REGION_HEIGHT
        max_lat = self.minY + (row_idx+1) * self.REGION_HEIGHT
        return min_long, min_lat, max_long, max_lat

    # 生成坐标
    def generateCoordinate(self, region_id):
        min_long, min_lat, max_long, max_lat = self.getRegionRange(region_id)
        # 生成经纬度
        longitude = np.random.uniform(min_long, max_long)
        latitude = np.random.uniform(min_lat, max_lat)
        return longitude, latitude

    # 转移矩阵 transform_matrix[2,0] = 1表示从区域2到区域0的taxi数为1
    def computeProbability(self, df):
        self.add_region(df)
        transform_matrix = np.zeros(
            (self.ROW_NUM*self.COL_NUM, self.ROW_NUM*self.COL_NUM))
        res = df.groupby(by='pickup_region')['dropoff_region'].value_counts()
        keys = res.index
        values = res.values
        for (idx, key) in enumerate(keys):
            x, y = key
            transform_matrix[x][y] = values[idx]
        transform_df = pd.DataFrame(transform_matrix)
        # 统计每个区域的请求起点数量
        pickup_counts = transform_df.apply(np.sum, axis=1)
        # 转移概率矩阵
        self.probability_df = transform_df.div(pickup_counts, axis=0)
        self.pickup_counts = pickup_counts

    # 生成locations
    def generateLocations(self, total_num):

        arr = np.zeros((total_num, 4))
        org_num = np.zeros(total_num)  # 每个请求的起点区域
        n = 0

        while n < total_num:
            # 选择一个区域生成请求
            origin_rid = np.random.randint(0, 121)
            if self.pickup_counts[origin_rid] == 0:
                continue
            # 在该区域内生成的请求数量（满足泊松分布）
            request_num = np.random.poisson(
                np.ceil(self.pickup_counts[origin_rid]/30))
            if request_num == 0:
                continue
            if n + request_num > total_num:
                request_num = total_num - n
            org_num[n:n+request_num] = np.array([origin_rid]*request_num)
            n += request_num

        # 生成坐标
        for i in range(total_num):
            # 生成起点坐标
            pickup_longitude, pickup_latitude = self.generateCoordinate(
                org_num[i])
            # 生成终点坐标
            dest_rid = self.getDestRegionId(org_num[i])
            dropoff_longitude, dropoff_latitude = self.generateCoordinate(
                dest_rid)
            arr[i] = [pickup_longitude, pickup_latitude,
                      dropoff_longitude, dropoff_latitude]

        df = pd.DataFrame(arr, columns=[
                          'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude'])
        df = df.sample(frac=1).reset_index(drop=True)
        df = df.round(5)
        return df

    def generateRequests(self, total_num, flag):
        # generate origins and destinations
        df = self.generateLocations(total_num)
        # flag == 1: generate random number seats for passengers
        if flag:
            seatNum = np.random.randint(1, 3, total_num)
        # flag == 0: generate fixed number seats (seat = 5) for drivers
        else:
            seatNum = 5
        df['seatNum'] = seatNum
        return df


if __name__ == '__main__':
    # filepath: 原始数据文件
    # leftbottom：整个区域范围左下角(longitude, latitude)
    # regionShape：整个区域划分为(row,col)
    # squreSize：一个小正方形的宽度和高度(width, height)
    G = Generator(filepath='./taxi2.txt', leftbottom=(116.3300873,
                  39.8463525), regionShape=(11, 11), squreSize=(0.010109, 0.010109))
    df = G.generateRequests(total_num=10, waitTime=5,
                            detourRatio=5, isRandom=True)
    print(df)
