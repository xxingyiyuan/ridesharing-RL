from DQNPriority import DQNPrioritizedReplay
from environmentDRL import Environment
from tool import Tool
from tqdm import tqdm
import numpy as np
from time import *


class AlgorithmDRL:
    def __init__(self, drivers_demand, passengers_demand):
        self.env = Environment(drivers_demand, passengers_demand)
        self.n_actions = len(self.env.candidateActions)
        self.n_features = len(passengers_demand)
        self.train()

    def train(self):
        env = self.env
        MEMORY_SIZE = 10000
        RL = DQNPrioritizedReplay(
            n_actions=self.n_actions, n_features=self.n_features, learning_rate=0.0002, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=0.00005, memory_size=MEMORY_SIZE)
        train_base = 10
        train_bais = MEMORY_SIZE
        episodes = 20000
        total_steps = 0
        epi_accumuReward = []
        opt = 0
        for _ in tqdm(range(episodes)):
            observation, curPassUti = env.resetEnv()
            step = 0
            maxUti = 0
            accumuReward = 0
            while True:
                # choose action by epsilon-greedy policy
                validIndex = env.candidateIndex
                actionIndex = RL.choose_action(observation, validIndex)
                action = env.candidateActions[actionIndex]
                # execute action
                observation_, reward, flag = env.step(action)
                # store transition
                RL.store_transition(
                    observation, actionIndex, reward, observation_)
                # update model
                if total_steps >= train_bais and total_steps % train_base == 0:
                    RL.learn()
                total_steps += 1
                step += 1

                curPassUti = env.getPassTotalUtility()
                if curPassUti > maxUti:
                    maxUti = curPassUti
                accumuReward += reward

                if flag == 2:
                    break
                if flag == 1:
                    if maxUti > opt:
                        opt = maxUti
                    epi_accumuReward.append(accumuReward)
                    break
                observation = observation_
        self.opt = opt

    def getTotalUtility(self):
        return self.opt
