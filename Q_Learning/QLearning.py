import random

class QLearningTable:
    def __init__(self, actions, learning_rate=0.1, reward_decay=0.9, e_greedy=0.9):
        self.actions = actions              # [0,1,2,3]
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q = {}                     

    def choose_action(self, state):
        self.check_state_exist(state)

        if random.random() < self.epsilon:
            q_list = self.q[state]
            max_q = max(q_list)
            best_actions = [i for i, q in enumerate(q_list) if q == max_q]
            action = random.choice(best_actions)
        else:
            action = random.choice(self.actions)

        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        q_predict = self.q[s][a]

        if s_ != 'terminal':
            q_target = r + self.gamma * max(self.q[s_])
        else:
            q_target = r

        self.q[s][a] += self.lr * (q_target - q_predict)

    def check_state_exist(self, state):
        if state not in self.q:
            self.q[state] = [0.0 for _ in self.actions]
