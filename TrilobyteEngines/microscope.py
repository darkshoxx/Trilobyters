# ALL MOVE PAIRS ARE STORED (X,Y), (HORIZONTAL,VERTICAL), (ROW, COLUMN) (board[somehing][here], something)
from copy import deepcopy

class Board:
    def __init__(self, blues:list[tuple[int,int]]=None, greens:list[tuple[int,int]]=None, blue_turn:bool=None) -> None:
        self.board = [ [0]*7 for _ in range(7)]
        if blues is not None:
            self.blues = blues
        else:
            self.blues = [(0,0),(6,6)]
        if greens is not None:
            self.greens = greens
        else:
            self.greens = [(0,6),(6,0)]
        self.populate()
        if blue_turn is not None:
            self.blue_turn = blue_turn
        else:
            self.blue_turn = True

    def capturing_offsets(self, index) -> list[int]:
        if index == 0:
            return [0,1]
        elif index == 6:
            return [-1,0]
        return [-1,0,1]

    def reaching_offsets(self, index) -> list[int]:
        if index == 0:
            return [0,1,2]
        elif index == 1:
            return [-1,0,1,2]
        elif index == 5:
            return [-2,-1,0,1]
        elif index == 6:
            return [-2,-1,0]
        return [-2,-1,0,1,2]
            
    def is_jump(self, off_x, off_y) -> bool:
        if abs(off_x)<2 and abs(off_y)<2:
            return False
        return True
    
    def m_type(self, off_x, off_y) -> str:
        if self.is_jump(off_x, off_y):
            return "J"
        return "D"

    def reaches(self, position) -> tuple[str,int,int]:
        pos_x, pos_y = position
        x_offsets = self.reaching_offsets(pos_x)
        y_offsets = self.reaching_offsets(pos_y)
        return [(self.m_type(off_x, off_y), pos_x + off_x,pos_y+off_y) for off_x in x_offsets for off_y in y_offsets if (off_x!=0 or off_y!=0)]

    def unblocked_reaches(self, position, board=None)-> tuple[str,int,int]:
        if board is None:
            board = self.board
        legal_moves = []
        for entry in self.reaches(position):
            if board[entry[2]][entry[1]] == 0:
                legal_moves.append(entry)
        return legal_moves

    def test_move(self, position, move, test_board) -> list[list[int]]:
        if self.blue_turn:
            player = 1
            opponent = 2
        else:
            player = 2
            opponent = 1
        pos_x, pos_y = position
        if move[0] == "J":
            test_board[pos_y][pos_x] = 0
        move_x = move[1]
        move_y = move[2]
        test_board[move_y][move_x] = player
        for off_x in self.capturing_offsets(move_x):
            for off_y in self.capturing_offsets(move_y):
                if off_x != 0 or off_y != 0:
                    if test_board[move_y + off_y][move_x + off_x] == opponent:
                        test_board[move_y + off_y][move_x + off_x] = player
        return test_board

    def execute_move(self, position, move) -> None:
        if self.blue_turn:
            player = 1
            opponent = 2
        else:
            player = 2
            opponent = 1
        pos_x, pos_y = position
        if move[0] == "J":
            self.board[pos_y][pos_x] = 0
        move_x = move[1]
        move_y = move[2]
        self.board[move_y][move_x] = player
        for off_x in self.capturing_offsets(move_x):
            for off_y in self.capturing_offsets(move_y):
                if off_x != 0 or off_y != 0:
                    if self.board[move_y + off_y][move_x + off_x] == opponent:
                        self.board[move_y + off_y][move_x + off_x] = player
        self.blue_turn = not self.blue_turn

    def execute_move_on_board(self, board,  position, move, maximizing_player) -> None:
        if maximizing_player:
            player = 1
            opponent = 2
        else:
            player = 2
            opponent = 1
        pos_x, pos_y = position
        if move[0] == "J":
            board[pos_y][pos_x] = 0
        move_x = move[1]
        move_y = move[2]
        board[move_y][move_x] = player
        for off_x in self.capturing_offsets(move_x):
            for off_y in self.capturing_offsets(move_y):
                if off_x != 0 or off_y != 0:
                    if board[move_y + off_y][move_x + off_x] == opponent:
                        board[move_y + off_y][move_x + off_x] = player

    
    def populate(self) -> None:
        for x,y in self.blues:
            self.board[y][x] = 1
        for x,y in self.greens:
            self.board[y][x] = 2

    def get_positions(self, board = None) -> tuple[list[int],list[int]]:
        if board is None:
            board = self.board
        blue_list = []
        green_list = []
        for y in range(7):
            row = board[y]
            for x in range(7):
                entry = row[x]
                if entry == 1:
                    blue_list.append((x, y))
                elif entry == 2:
                    green_list.append((x, y))
        return blue_list, green_list

    def get_score(self, board = None) -> tuple[int,int]:
        blue_list, green_list = self.get_positions(board = board)
        score_blue = len(blue_list)
        score_green = len(green_list)
        return (score_blue, score_green)

    def score_move(self, position, move, board = None) -> int:
        if board is None:
            board = self.board
        current_blue, current_green = self.get_score(board)
        board_copy = deepcopy(board)
        test_board = self.test_move(position, move, board_copy)
        new_blue, new_green = self.get_score(test_board)
        blue_score = new_blue - current_blue - new_green + current_green
        # if self.blue_turn:
        #     return blue_score
        # else:
        #     return -blue_score
        return blue_score
        
    def score_unply(self, position, move) -> int:
        from copy import deepcopy
        current_blue, current_green = self.get_score()
        board_copy = deepcopy(self.board)
        test_board = self.test_move(position, move, board_copy)
        new_blue, new_green = self.get_score(test_board)
        blue_score = new_blue - current_blue - new_green + current_green
        if self.blue_turn:
            own_score = blue_score
        else:
            own_score = -blue_score
        self.blue_turn = not self.blue_turn
        legal_moves = self.get_legal_moves(test_board)
        worst_response = 50
        for move in legal_moves:
            current_response_score = self.score_move(move[0], move[1], test_board)
            if current_response_score < worst_response:
                worst_response = current_response_score
        return own_score + worst_response 

    def get_legal_moves(self, test_board=None, maximizing_player = None) -> list[tuple[tuple,tuple]]:
        if test_board is None:
            test_board = self.board
        if maximizing_player is None:
            maximizing_player = self.blue_turn
        blue_list, green_list = self.get_positions(board = test_board)
        if maximizing_player:
            position_list = blue_list
        else:
            position_list = green_list
        legal_moves = []
        for position in position_list:
            for unblocked_reach in self.unblocked_reaches(position, test_board):
                legal_moves.append((position, unblocked_reach))
        return legal_moves     



    def fill(self):
        """ FOR TESTING ONLY DO NOT CALL"""
        import random
        self.board = [random.sample([1,1,1,1,1,2,2,2,2,2],7)]*7

    def __repr__(self):
        return_list = [str(line) + "\n" for line in self.board]
        score_blue, score_green = self.get_score()
        return_list += [f"blue: {score_blue} \ngreen: {score_green}"]
        if score_blue + score_green == 49:
            if score_blue > score_green:
                return_list += ["\nA WINNER IS BLUE"]
            else:
                return_list += ["\nA WINNER IS GREEN"]
                
        return "".join(return_list)


    def stateval(self, board) -> int:
        blue, green = self.get_score(board)
        return blue - green

    def minimax(self, depth, maximizing_player, board=None) -> int:
        if board is None:
            board = self.board
        legal_moves = self.get_legal_moves(board, maximizing_player)

        
        if depth == 0 or legal_moves == []:
            return self.stateval(board)
        

        if maximizing_player:
            max_eval = -100
            for move in legal_moves:
                position, reach = move
                candidate_board = deepcopy(board)
                self.execute_move_on_board(candidate_board, position, reach, maximizing_player)
                eval_temp = self.minimax(depth - 1, False, candidate_board)
                max_eval = max(max_eval, eval_temp)
            return max_eval
        
        else:
            min_eval = 100
            for move in legal_moves:
                position, reach = move
                candidate_board = deepcopy(board)
                self.execute_move_on_board(candidate_board, position, reach, maximizing_player)
                eval_temp = self.minimax(depth - 1, True, candidate_board)
                min_eval = min(eval_temp, min_eval)
            return min_eval
            

    def minimax_prune(self, depth, alpha, beta, maximizing_player, board=None) -> int:
        if board is None:
            board = self.board
        legal_moves = self.get_legal_moves(board, maximizing_player)

        
        if depth == 0 or legal_moves == []:
            return self.stateval(board)
        

        if maximizing_player:
            max_eval = -100
            for move in legal_moves:
                position, reach = move
                candidate_board = deepcopy(board)
                self.execute_move_on_board(candidate_board, position, reach, maximizing_player)
                eval_temp = self.minimax_prune(depth - 1, alpha, beta, False, candidate_board)
                max_eval = max(max_eval, eval_temp)
                alpha = max(alpha, eval_temp)
                if beta <= alpha:
                    break
            return max_eval
        
        else:
            min_eval = 100
            for move in legal_moves:
                position, reach = move
                candidate_board = deepcopy(board)
                self.execute_move_on_board(candidate_board, position, reach, maximizing_player)
                eval_temp = self.minimax_prune(depth - 1, alpha, beta, True, candidate_board)
                min_eval = min(eval_temp, min_eval)
                beta = min(beta, eval_temp)
                if beta <= alpha:
                    break
            return min_eval
    
    def find_best_move(self, depth, maximizing_player, board=None):
        if board is None:
            board = self.board
        legal_moves = self.get_legal_moves(board, maximizing_player)
        return_list = []
        for move in legal_moves:
            position, reach = move
            candidate_board = deepcopy(board)
            self.execute_move_on_board(candidate_board, position, reach, maximizing_player)
            score = self.minimax_prune(depth, -100, 100, False, candidate_board)
            return_list.append((score, position, reach))
        return "".join(str(item) + "\n" for item in return_list)

if __name__ == "__main__":
    # b = Board()
    # print(b.score_unply((0,0),("J",5,0)))
    # print(b.minimax(depth=4,maximizing_player=True))
    # print(b.minimax_prune(depth=4, alpha=-100, beta=100, maximizing_player=True))

    # easy_board = Board([(0,0)],[(3,0)], True)
    # print(easy_board.get_score())
    # print(easy_board.get_legal_moves())
    # print(easy_board.minimax(depth=4,maximizing_player=True))
    # print(easy_board.find_best_move(depth=4, maximizing_player=True))
    # dxn_board = Board([(0,5),(0,6),(1,5),(2,2), (6,6)],[(6,0),(6,1),(6,2)], True)
    # print(dxn_board.find_best_move(depth=3, maximizing_player=True))

    default_board = Board()
    # print(default_board.find_best_move(depth=4, maximizing_player=True))
    default_board.execute_move((0, 0), ('D', 1, 0))
    default_board.execute_move((6, 0), ('D', 6, 1))
    default_board.execute_move((6, 6), ('D', 5, 6))
    default_board.execute_move((6, 0), ('D', 5, 0))
    print(default_board)
    print(default_board.find_best_move(depth=3, maximizing_player=True))