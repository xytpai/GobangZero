# @ref: https://github.com/junxiaosong/AlphaZero_Gomoku/blob/master/game.py
import numpy as np


class Board(object):
    def __init__(self, **kwargs):
        self.height = int(kwargs.get('height', 8))
        self.width = int(kwargs.get('width', 8))
        self.n = int(kwargs.get('n', 5))
        # check
        if self.height < self.n or self.width < self.n:
            raise Exception('board height and width can not be '
                                'less than {}'.format(self.n))
        
    def init_board(self, start_player=0):
        # player0, player1, last move, which player(0 or 1)
        self.state = np.zeros((4, self.height, self.width))
        self.cur_player = start_player
        self.num_piece = 0
    
    def current_state(self):
        return self.state
    
    def do_move(self, move):
        y, x = move
        if self.state[0, y, x] == 1 or self.state[1, y, x] == 1:
            return False
        self.state[self.cur_player, y, x] = 1
        self.state[2, :, :] = 0
        self.state[2, y, x] = 1
        self.state[3, :, :] = self.cur_player
        self.last_player = self.cur_player
        self.last_move = move
        self.cur_player = 1 if self.cur_player==0 else 0
        self.num_piece += 1
        return True
        
    def has_a_winner(self):
        height, width, n = self.height, self.width, self.n
        y, x = self.last_move
        player = self.last_player
        if (x in range(width - n + 1) and
                len(set(states.get(i, -1) for i in range(m, m + n))) == 1):
            return True, player
        if (y in range(height - n + 1) and
                len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
            return True, player
        if (x in range(width - n + 1) and y in range(height - n + 1) and
                len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
            return True, player
        if (x in range(n - 1, width) and y in range(height - n + 1) and
                len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
            return True, player
        return False, -1
    
    def game_end(self):
        win, winner = self.has_a_winner()
        if win:
            return True, winner
        elif self.num_piece >= self.height*self.width:
            return True, -1
        return False, -1
    
    def get_current_player(self):
        return self.cur_player


class Game(object):
    def __init__(self, board, **kwargs):
        self.board = board
    
    def graphic(self):
        board = self.board
        height = board.height
        width = board.width
        print("Player0", "with O".rjust(3))
        print("Player1", "with X".rjust(3))
        print()
        for x in range(width):
            print("{0:8}".format(x), end='')
        print('\r\n')
        for y in range(height):
            print("{0:4d}".format(y), end='')
            for x in range(width):
                p0 = int(board.state[0, y, x])
                p1 = int(board.state[1, y, x])
                if p0 == 1: print('O'.center(8), end='')
                elif p1 == 1: print('X'.center(8), end='')
                else: print('_'.center(8), end='')
            print('\r\n\r\n')

    def start_play(self, players, start_player=0, is_shown=True):
        self.board.init_board(start_player)
        if is_shown:
            self.graphic()
        while True:
            current_player = self.board.get_current_player()
            move = players[current_player].get_action(self.board)
            self.board.do_move(move)
            if is_shown:
                self.graphic()
            end, winner = self.board.game_end()
            if end:
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is Player ", winner)
                    else:
                        print("Game end. Tie")
                return winner
    
    # FIXME
    def start_self_play(self, player, is_shown=False):
        self.board.init_board()
        states, mcts_probs, current_players = [], [], []
        while True:
            move, move_probs = player.get_action(self.board, return_prob=1)
            # store the data
            states.append(self.board.current_state())
            mcts_probs.append(move_probs)
            current_players.append(self.board.get_current_player())
            # perform a move
            self.board.do_move(move)
            if is_shown:
                self.graphic()
            end, winner = self.board.game_end()
            if end:
                # winner from the perspective of the current player of each state
                winners_z = np.zeros(len(current_players))
                if winner != -1:
                    winners_z[np.array(current_players) == winner] = 1.0
                    winners_z[np.array(current_players) != winner] = -1.0
                # reset MCTS root node
                player.reset_player()
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is player:", winner)
                    else:
                        print("Game end. Tie")
                return winner, zip(states, mcts_probs, winners_z)


if __name__ == '__main__':
    board = Board()
    game = Game(board)
    game.graphic()
