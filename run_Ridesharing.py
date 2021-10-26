from DQNPriority import DQNPrioritizedReplay
from environment import Environment
from tool import Tool
import numpy as np

drivers_num, passengers_num = 10, 20
env = Environment(drivers_num=drivers_num, passengers_num=passengers_num)
n_actions = len(env.candidateActions)
n_features = passengers_num + 1
MEMORY_SIZE = 5000
RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=None, memory_size=MEMORY_SIZE)
train_base = 10
train_bais = MEMORY_SIZE
# (driver_num, passenger_num) initassignment CFA
# (5,10) 61.72 61.72
# (10, 20) 116 116
# (30, 60) 107 120
# (50, 100) 
# (300, 600) 2611 3033


def train():
    total_steps = 0
    episodes = 1000
    epi_maxUti = []
    opt_stepUti = None
    opt = 0
    maxStep = 1500
    print('candidateActions:{}'.format(len(env.candidateActions)))
    print(env.passUti)
    for i in range(episodes):
        observation, curPassUti = env.resetEnv()
        step = 0
        maxUti = 0
        stepUti = []
        observation = np.append(observation, step)
        while step < maxStep:

            total_steps += 1
            step += 1
            # choose action by epsilon-greedy policy
            actionIndex = RL.choose_action(observation)
            action = env.candidateActions[actionIndex]
            # execute action
            observation_, reward, flag = env.step(action)
            observation_ = np.append(observation_, step)
            RL.store_transition(
                observation, actionIndex, reward, observation_)
            # update model
            if total_steps >= train_bais and total_steps % train_base == 0:
                RL.learn()

            curPassUti = env.getPassTotalUtility()
            stepUti.append(curPassUti)
            if curPassUti > maxUti:
                maxUti = curPassUti
                # print('episodes: {}, steps: {}, maxUti: {}'.format(i, step, maxUti))

            if step == maxStep:

                if maxUti > opt:
                    opt = maxUti
                    opt_stepUti = stepUti
                print('episodes: {}, steps: {}, maxUti: {}, totalSteps: {}, opt: {}'.format(
                    i, step, maxUti, total_steps, opt))
                break
            observation = observation_

        epi_maxUti.append(maxUti)

    Tool.plotData(RL.cost_his, ('step', 'cost'))
    Tool.plotData(epi_maxUti, ('episode', 'maxUti'))
    # Tool.plotData(opt_stepUti,('step','stepUti'))
    # Tool.plotData(env.totalReward,('step','reward'))
    Tool.pltShow()


if __name__ == '__main__':
    train()
