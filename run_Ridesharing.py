from DQNPriority import DQNPrioritizedReplay
from environment import Environment


drivers_num, passengers_num = 50, 100
env = Environment(drivers_num=drivers_num, passengers_num=passengers_num)
n_actions = len(env.candidateActions)
n_features = passengers_num
MEMORY_SIZE = 10000
RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.005, reward_decay=1, e_greedy=0.9, e_greedy_increment=0.0002, memory_size=MEMORY_SIZE)
train_base = 5
train_bais = MEMORY_SIZE


def train():
    total_steps = 0
    episodes = 10
    epi_maxUti = []
    opt_stepUti = None
    opt = 0
    maxStep = 10000

    for i in range(episodes):
        observation, curPassUti = env.resetEnv()
        step = 0
        maxUti = 0
        count = 0
        stepUti = []
        while step < maxStep:

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

            curPassUti = env.getPassTotalUtility()
            stepUti.append(curPassUti)
            if curPassUti > maxUti:
                count = 0
                maxUti = curPassUti
                # print('episodes: {}, steps: {}, maxUti: {}'.format(i, step, maxUti))
            else:
                count += 1

            if step == maxStep:

                if maxUti > opt:
                    opt = maxUti
                    opt_stepUti = stepUti
                print('episodes: {}, steps: {}, maxUti: {}, totalSteps: {}, opt: {}'.format(
                    i, step, maxUti, total_steps, opt))
                break
            observation = observation_

        epi_maxUti.append(maxUti)

    print(epi_maxUti)
    print(RL.epsilon)
    RL.plot_cost(RL.cost_his)
    RL.plot_utility(opt_stepUti)
    # RL.plot_utility(epi_maxUti)


if __name__ == '__main__':
    train()
