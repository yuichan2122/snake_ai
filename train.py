import snake
import agent
import numpy as np


def get_state(location_history, food_location):
    state = [([0] * 3) for i in range(49)]
    state[location_history[-1]][0] = 1  # location of head
    for location in location_history[0:-1]:
        state[location][1] = 1  # location of body
    state[food_location][2] = 1
    state = np.array(state).flatten()

    board = [0] * 49
    length = len(location_history)
    for n, i in enumerate(location_history):
        board[i] = ((length / 100) - 1) - ((n + 1) / 100)
    board[food_location] = 1
    return np.array([state]), np.array([board])


def get_event(location_history, food_location):
    possible_actions = 4
    events = []
    state, _ = get_state(location_history, food_location)
    game_e = snake.snake()
    for action in range(possible_actions):
        game_e.location_history = location_history[:]
        game_e.food_location = food_location
        game_e.snake_length = max(len(location_history), 3)
        result = game_e.play(action)
        reward = get_reward(result)
        if reward == -1:
            done = True
            events.append([None, action, reward, None, done])
        else:
            next_state, _ = get_state(game_e.location_history, game_e.food_location)
            done = False
            events.append([None, action, reward, next_state[:], done])

    events[0][0] = state
    return events


def get_reward(result):
    if 'move' in result:
        return 0
    if 'food' in result:
        return 1
    if 'invalid' in result:
        return -1


def test(model):
    game_test = snake.snake()
    end = False
    move = 0
    while not end:
        current_food = game_test.food_location
        state, _ = get_state(game_test.location_history, game_test.food_location)
        prediction = model.predict(state)[0]
        action = np.argmax(prediction)
        result = game_test.play(action)
        print(f'     {int(prediction[0]*1000)}')
        print(f'{int(prediction[1]*1000)}  {move} {int(prediction[3]*1000)}')
        print(f'     {int(prediction[2]*1000)}')
        game_test.print_board()
        if current_food != game_test.food_location:
            move = 0
        else:
            move += 1
        if result == 'invalid' or move > 50:
            end = True


def train():
    ai = agent.Agent(147, 4, model_name=name)
    game_n = 0
    while True:
        game = snake.snake()
        end = False
        move = 0
        game_n += 1
        print(game_n, len(ai.memory), end='\r')
        while not end:
            current_history = game.location_history[:]
            current_food = game.food_location
            state, board = get_state(current_history, current_food)
            action = ai.act(state, board)
            result = game.play(action)
            ai.memory.append(get_event(current_history, current_food))
            if current_food != game.food_location:
                move = 0
            else:
                move += 1
            if result == 'invalid' or move > 50:
                end = True
        if game_n % 3000 == 0:
            ai.exp_replay()
            test(ai.model)
            ai.model.save(f'model/{name}_{game_n}')


name = 'd'
train()
