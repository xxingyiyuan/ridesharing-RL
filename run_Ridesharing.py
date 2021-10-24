from DQNPriority import DQNPrioritizedReplay
from environment import Environment


drivers_num, passengers_num = 50, 100
env = Environment(drivers_num=drivers_num, passengers_num=passengers_num)
n_actions = len(env.candidateActions)
n_features = passengers_num
MEMORY_SIZE = 10000
RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.005, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=0.00005, memory_size=MEMORY_SIZE)
train_base = 5
train_bais = MEMORY_SIZE


def train():
    total_steps = 0
    episodes = 5
    epi_maxUti = []
    opt = 0
    

    for i in range(episodes):
        observation, curPassUti = env.resetEnv()
        step = 0
        maxUti = 0
        count = 0
        stepUti = []
        stepCost = [] 
        while True:

            total_steps += 1
            step += 1
            # choose action by epsilon-greedy policy
            actionIndex = RL.choose_action(observation)
            action = env.candidateActions[actionIndex]
            # execute action
            observation_, reward, flag = env.step(action)
            RL.store_transition(
                    observation, actionIndex, reward, observation_)
            # update model
            if total_steps >= train_bais and total_steps % train_base == 0:
                RL.learn()
                stepCost.append(RL.cost)

            curPassUti = env.getPassTotalUtility()
            if curPassUti > maxUti:
                count = 0
                maxUti = curPassUti
                if maxUti > opt:
                    opt = maxUti
                # print('episodes: {}, action:{}, steps: {}, curPassUti: {}, maxUti: {}, totalSteps: {}, opt: {}'.format(i, action, step, curPassUti, maxUti, total_steps, opt))
            else:
                count += 1
            stepUti.append(curPassUti)

            if count > 5000:
                print('episodes: {}, steps: {}, maxUti: {}, totalSteps: {}, opt: {}'.format(
                    i, step, maxUti, total_steps, opt))
                break
            observation = observation_
        RL.plot_cost(stepCost)
        RL.plot_utility(stepUti)
        epi_maxUti.append(maxUti)

    print(epi_maxUti)
    RL.plot_cost(RL.cost_his)
    RL.plot_utility(epi_maxUti)


if __name__ == '__main__':
    train()
