```python
drivers_num, passengers_num = 30, 60
env = Environment(drivers_num=drivers_num, passengers_num=passengers_num)
n_actions = len(env.candidateActions)
n_features = passengers_num

MEMORY_SIZE = 5000
RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.0002, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=0.00005, memory_size=MEMORY_SIZE)
train_base = 3
train_bais = MEMORY_SIZE
```

<img src="1028-result.assets/image-20211028180128205.png" alt="image-20211028180128205"  /><img src="1028-result.assets/image-20211028180147485.png" alt="image-20211028180147485"  />

```python
# requests_1
drivers_num, passengers_num = 50, 100
env = Environment(drivers_num=drivers_num, passengers_num=passengers_num)
n_actions = len(env.candidateActions)
n_features = passengers_num

MEMORY_SIZE = 5000
RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.0002, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=0.00005, memory_size=MEMORY_SIZE)
train_base = 5
train_bais = MEMORY_SIZE
```

```
episode = 20000
CFA: 135.14646783962678
DRL: 216.27114426730228
```

![image-20211028200714743](1028-result.assets/image-20211028200714743.png)



![image-20211028200652751](1028-result.assets/image-20211028200652751.png)

```python
# requests_2 调整train_base
drivers_num, passengers_num = 50, 100
env = Environment(drivers_num=drivers_num, passengers_num=passengers_num)
n_actions = len(env.candidateActions)
n_features = passengers_num

MEMORY_SIZE = 5000
RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.0002, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=0.00005, memory_size=MEMORY_SIZE)
train_base = 10
train_bais = MEMORY_SIZE
```

![image-20211028232425853](1028-result.assets/image-20211028232425853.png)

![image-20211028232501439](1028-result.assets/image-20211028232501439.png)

```python
# requests_3 调整MEMORY_SIZE
drivers_num, passengers_num = 50, 100
env = Environment(drivers_num=drivers_num, passengers_num=passengers_num)
n_actions = len(env.candidateActions)
n_features = passengers_num

MEMORY_SIZE = 10000
RL = DQNPrioritizedReplay(
    n_actions=n_actions, n_features=n_features, learning_rate=0.0002, reward_decay=0.9, e_greedy=0.9, e_greedy_increment=0.00005, memory_size=MEMORY_SIZE)
train_base = 10
train_bais = MEMORY_SIZE
```

![image-20211028234234981](1028-result.assets/image-20211028234234981.png)

![image-20211028234301926](1028-result.assets/image-20211028234301926.png)

requests_4: 107.99

![image-20211029000021046](1028-result.assets/image-20211029000021046.png)

![image-20211028235925352](1028-result.assets/image-20211028235925352.png)

requests_5: 169.1

![image-20211029002523963](1028-result.assets/image-20211029002523963.png)

![image-20211029002546585](1028-result.assets/image-20211029002546585.png)