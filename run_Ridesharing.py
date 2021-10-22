from DQNPriority import DQNPrioritizedReplay
from environment import Environment


drivers_num, passengers_num = 50, 100
n_actions = passengers_num * (drivers_num + 1)
n_features = passengers_num

env = Environment(drivers_num=drivers_num, passengers_num=passengers_num)

RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=0.0002)
train_base = 3.0
train_bais = 30.0


def train():
    total_steps = 0
    episodes = 10
    epi_maxUti = []
    opt = 0
    for i in range(1, episodes):
        observation, curPassUti = env.resetEnv()
        step = 0
        maxUti = 0
        while True:
            total_steps += 1
            step += 1
            # choose action by epsilon-greedy policy
            action = RL.choose_action(observation, env.candidateActions)
            # execute action
            observation_, reward, done = env.step(action)
            RL.store_transition(observation, action, reward, observation_)
            if done:
                break
            # update model
            if total_steps >= train_bais and total_steps % train_base == 0:
                RL.learn()
            curPassUti = env.getPassTotalUtility()
            if curPassUti > maxUti:
                maxUti = curPassUti
                if maxUti > opt:
                    opt = maxUti
                print('episodes: {}, action:{}, steps: {}, curPassUti: {}, maxUti: {}, totalSteps: {}, opt: {}'.format(
                i, action, step, curPassUti, maxUti, total_steps, opt))
            observation = observation_
        epi_maxUti.append(maxUti)
    print(epi_maxUti)


if __name__ == '__main__':
    train()
