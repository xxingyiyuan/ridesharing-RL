from DQNPriority import DQNPrioritizedReplay
from environment import Environment
from tool import Tool
from tqdm import tqdm
import numpy as np
from time import *
file_num = 9
drivers_num, passengers_num = 40, 80
env = Environment(drivers_num=drivers_num,
                  passengers_num=passengers_num, detourRatio=0.5, waitTime=5, file_num=file_num)
n_actions = len(env.candidateActions)
n_features = passengers_num

MEMORY_SIZE = 10000
RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.0002, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=0.00005, memory_size=MEMORY_SIZE)
train_base = 10
train_bais = MEMORY_SIZE
episodes = 20000

def train():
    total_steps = 0
    epi_maxUti = []
    epi_accumuReward = []
    opt = 0
    print('candidateActions:{}'.format(len(env.candidateActions)))
    epi_time = []
    for i in tqdm(range(episodes)):

        observation, curPassUti = env.resetEnv()
        step = 0
        maxUti = 0
        # observation = np.append(observation, step)
        accumuReward = 0
        begin_time = time()
        while True:
            # choose action by epsilon-greedy policy
            validIndex = env.candidateIndex
            actionIndex = RL.choose_action(observation, validIndex)
            action = env.candidateActions[actionIndex]
            # execute action
            observation_, reward, flag = env.step(action)
            # observation_ = np.append(observation_, step)
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
                # print('episodes: {}, steps: {}, lastUti: {}, accumuReward: {}, totalSteps: {}, opt: {}'.format(
                    # i, step, curPassUti, accumuReward, total_steps, opt))
                break
            if flag == 1:
                if maxUti > opt:
                    opt = maxUti
                end_time = time()
                epi_time.append(end_time - begin_time)
                epi_maxUti.append(maxUti)
                epi_accumuReward.append(accumuReward)

                # print('episodes: {}, steps: {}, lastUti: {}, accumuReward: {}, totalSteps: {}, opt: {}'.format(
                #     i, step, curPassUti, accumuReward, total_steps, opt))
                break
            observation = observation_
    print(np.mean(epi_time))    
    print(opt,total_steps)
    # Tool.storeData(RL.cost_his, 'cost_{}'.format(file_num))
    # Tool.storeData(epi_accumuReward, 'reward_{}'.format(file_num))
    # Tool.plotData(epi_accumuReward, ('Episode', 'Reward'),
    #               'requests_{}_accumuReward'.format(file_num))
    # Tool.plotData(RL.cost_his, ('Step', 'Loss'),
    #               'requests_{}_cost'.format(file_num))
    # Tool.pltShow()


if __name__ == '__main__':
    train()
