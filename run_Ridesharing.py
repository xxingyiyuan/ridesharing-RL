from DQNPriority import DQNPrioritizedReplay
from environment import Environment
from tool import Tool
import numpy as np

drivers_num, passengers_num = 5, 10
env = Environment(drivers_num=drivers_num, passengers_num=passengers_num)
n_actions = len(env.candidateActions)
n_features = passengers_num + 1
MEMORY_SIZE = 3000
RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=0.001, memory_size=MEMORY_SIZE)
train_base = 10
train_bais = MEMORY_SIZE
# (driver_num, passenger_num) initassignment CFA
# (5,10) 61.72 61.72, 62.78
# (10, 20) 116 116, 120
# (30, 60) 107 120 random: 159 (step: 1000), 157
# (50, 100)
# (300, 600) 2611 3033


def train():
    total_steps = 0
    episodes = 3000
    epi_lastUti = []
    epi_maxUti = []
    epi_accumuReward = []
    epi_step = []
    opt = 0
    print('candidateActions:{}'.format(len(env.candidateActions)))

    for i in range(episodes):
        observation, curPassUti = env.resetEnv()
        step = 0
        maxUti = 0
        observation = np.append(observation, step)
        accumuReward = 0
        while True:
            validIndex = env.getVaildIndex()
            # choose action by epsilon-greedy policy
            actionIndex = RL.choose_action(observation, validIndex)
            action = env.candidateActions[actionIndex]
            # execute action
            observation_, reward, flag = env.step(action)
            observation_ = np.append(observation_, step)
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
                epi_lastUti.append(curPassUti)
                epi_maxUti.append(maxUti)
                epi_accumuReward.append(accumuReward)
                epi_step.append(step)
                print('episodes: {}, steps: {}, lastUti: {}, accumuReward: {}, totalSteps: {}, opt: {}'.format(
                    i, step, curPassUti, accumuReward, total_steps, opt))
                break
            observation = observation_

    Tool.plotData(RL.cost_his, ('step', 'cost'))
    # Tool.plotData(epi_step, ('episode', 'steps'))
    # Tool.plotData(epi_maxUti, ('episode', 'maxUti'))
    Tool.plotData(epi_lastUti, ('episode', 'lastUti'))
    Tool.plotData(epi_accumuReward, ('episode', 'accumureward'))
    Tool.pltShow()


if __name__ == '__main__':
    train()
