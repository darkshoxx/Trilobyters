from copy import deepcopy

def populate(board, blues, greens):
    for x,y in blues:
        board[y][x] = 1
    for x,y in greens:
        board[y][x] = 2

def get_tiles(position, max_player):
    tiles = []
    if max_player:
        player = 1
    else:
        player = 2
    for i in range(7):
        for j in range(7):
            if position[j][i] == player:
                tiles.append((i,j))
    return tiles

def reaching_offsets(index) -> list[int]:
    if index == 0:
        return [0,1,2]
    elif index == 1:
        return [-1,0,1,2]
    elif index == 5:
        return [-2,-1,0,1]
    elif index == 6:
        return [-2,-1,0]
    return [-2,-1,0,1,2]

def capturing_offsets(index) -> list[int]:
    if index == 0:
        return [0,1]
    elif index == 6:
        return [-1,0]
    return [-1,0,1]

# def direct_neighbours(tiles):
#     neighbours = []
#     for tile in tiles:
#         x_offsets = reaching_offsets(tile[0])
#         y_offsets = reaching_offsets(tile[1])
#         pass



def get_legal_moves(position, max_player):
    tiles = get_tiles(position, max_player)
    # neighbours = direct_neighbours(tiles)
    move_list = []
    for tile in tiles:
        x_pos = tile[0]
        y_pos = tile[1]
        x_offsets = reaching_offsets(x_pos)
        y_offsets = reaching_offsets(y_pos)
        for x_off in x_offsets:
            for y_off in y_offsets:
                # check non double zero
                if x_off!=0 or y_off!=0:
                    # check board empty
                    y_new = y_pos + y_off
                    x_new = x_pos + x_off
                    if position[y_new][x_new] == 0:
                        # if it's duplication, is it in the list yet?
                        if abs(x_off)<2 and abs(y_off)<2:
                            if (False, x_new, y_new) not in move_list:
                                move_list.append((False, x_new, y_new))
                        else:
                            move_list.append((True, x_new, y_new, x_pos, y_pos))
    return move_list
                        

def stat_eval(position):
    score = 0
    empty = 0
    for row in position:
        for entry in row:
            if entry == 1:
                score += 1
            elif entry == 2:
                score -= 1
            else:
                empty +=1
    return score, empty


def execute(move, position, max_player):
    if max_player:
        player = 1
        opponent = 2
    else:
        player = 2
        opponent = 1 
    x_pos, y_pos = move[1:3]
    if move[0]:
        x_old, y_old = move[3:5]
        position[y_old][x_old] = 0
    position[y_pos][x_pos] = player
    for x_off in capturing_offsets(x_pos):
        for y_off in capturing_offsets(y_pos):
            if x_off!= 0 or y_off != 0:
                if position[y_pos + y_off][x_pos + x_off] == opponent:
                    position[y_pos + y_off][x_pos + x_off] = player   

def execute_mp(move, position, max_player):
    execute(move, position, max_player)
    return position

def minimax(position, depth, alpha, beta, max_player):
    legal_moves = get_legal_moves(position, max_player)
    if depth == 0:
        if max_player:
            bias = 0.5
        else:
            bias = -0.5        
        score, _ = stat_eval(position)
        return score + bias
    if legal_moves == []:
        if max_player:
            bias = 0.5
        else:
            bias = -0.5        
        score, empty = stat_eval(position)
        if empty == 0:
            if score > 0:
                return 100
            return -100
        return score + bias*2*empty
    
    if max_player:
        max_eval = -100
        for move in legal_moves:
            child = deepcopy(position)
            execute(move, child, max_player)
            eval_temp = minimax(child, depth-1, alpha, beta, False)
            max_eval = max(max_eval, eval_temp)
            alpha = max(alpha, eval_temp)
            if beta <= alpha:
                break
        return max_eval
    
    min_eval = 100
    for move in legal_moves:
        child = deepcopy(position)
        execute(move, child, max_player)
        eval_temp = minimax(child, depth-1, alpha, beta, True)
        min_eval = min(min_eval, eval_temp)
        beta = min(beta, eval_temp)
        if beta <= alpha:
            break
    return min_eval

def printb(board):
    return_list = [str(line) + "\n" for line in board]
    # score_blue, score_green = self.get_score()
    # return_list += [f"blue: {score_blue} \ngreen: {score_green}"]
    # if score_blue + score_green == 49:
    #     if score_blue > score_green:
    #         return_list += ["\nA WINNER IS BLUE"]
    #     else:
    #         return_list += ["\nA WINNER IS GREEN"]
            
    print("".join(return_list))

def find_best_move(board, depth, maximizing_player):
    legal_moves = get_legal_moves(board, maximizing_player)
    return_list = []
    for move in legal_moves:
        candidate_board = deepcopy(board)
        execute(move, candidate_board, maximizing_player)
        score = minimax(candidate_board, depth-1, -100, 100, False)
        return_list.append((score, move))
    return "".join(str(item) + "\n" for item in return_list)

def minmaxhelper(move_tuple):
    move, board, depth = move_tuple
    score = minimax(board, depth-1, -100, 100, False)
    return score, move

def find_best_move_mp(board, depth, maximizing_player):
    from multiprocessing import Pool
    legal_moves = get_legal_moves(board, maximizing_player)
    return_list = []
    move_tuples = [(move,execute_mp(move,deepcopy(board),maximizing_player), depth) for move in legal_moves]

    with Pool(32) as p:
        score_tuple = p.map(minmaxhelper,move_tuples)
        return_list.append(score_tuple)
    return "".join(str(item) + "\n" for item in return_list[0])


if __name__ == "__main__":            
    blues = None # [(0,0)]
    greens = None # [(3,0)]    
    board = [ [0]*7 for _ in range(7)]
    if blues is not None:
        blues = blues
    else:
        blues = [(0,0),(6,6)]
    if greens is not None:
        greens = greens
    else:
        greens = [(0,6),(6,0)]
    populate(board, blues, greens)
    # print(get_legal_moves(board, True))
    # print(find_best_move_mp(board, 2, True))
    



    # print(stat_eval(board))
    # print(get_legal_moves(board, True))
    # print(minimax(board,3,-101,101,True))
    execute((False, 0, 1), board, True)
    execute((False, 5, 0), board, False)
    execute((False, 1, 0), board, True)
    execute((False, 6, 1), board, False)
    execute((False, 2, 0), board, True)
    execute((False, 4, 0), board, False)
    execute((False, 3, 0), board, True)
    execute((True, 3, 1, 5, 0), board, False)
    execute((False, 2, 1), board, True)
    execute((False, 4, 1), board, False)
    execute((False, 1, 1), board, True)
    execute((False, 5, 0), board, False)
    execute((False, 3, 2), board, True)
    execute((True, 2, 2, 4, 0), board, False)
    execute((False, 5, 1), board, True)
    execute((False, 4, 0), board, False)
    execute((False, 1, 2), board, True)
    execute((True, 1, 3, 3, 2), board, False)
    execute((False, 3, 2), board, True)
    execute((False, 4, 2), board, False)
    execute((False, 5, 2), board, True)
    execute((False, 0, 2), board, False)
    execute((False, 2, 3), board, True)
    execute((False, 0, 3), board, False)
    # crossroads between three 6.5 jumps and a 5.5 non-jump
    execute((True, 0, 4, 2, 3), board, True)
    execute((False, 2, 3), board, False)
    execute((False, 3, 3), board, True)
    execute((False, 1, 4), board, False)
    execute((False, 2, 4), board, True)
    execute((False, 1, 5), board, False)
    execute((True, 2, 5, 3, 3), board, True)
    execute((True, 6, 2, 5, 0), board, False)
    # crossroads between two 6.5 jumps and a 5.5 non-jump
    execute((True, 5, 0, 3, 2), board, True)
    execute((False, 3, 2), board, False)
    execute((False, 0, 5), board, True)
    execute((False, 3, 4), board, False)
    execute((True, 3, 5, 1, 3), board, True)
    execute((False, 1, 3), board, False)
    execute((False, 3, 3), board, True)
    execute((False, 4, 3), board, False)
    execute((True, 4, 4, 2, 2), board, True)
    execute((False, 2, 2), board, False)
    execute((False, 5, 3), board, True)
    execute((True, 1, 6, 0, 4), board, False)
    execute((False, 2, 6), board, True)
    execute((False, 0, 4), board, False)
    execute((False, 3, 6), board, True)
    execute((True, 6, 3, 4, 1), board, False)
    execute((False, 4, 1), board, True)
    execute((False, 5, 4), board, False)
    execute((True, 4, 5, 6, 6), board, True)
    execute((True, 5, 5, 6, 3), board, False)
    execute((False, 6, 3), board, True)
    execute((False, 6, 4), board, False)
    execute((True, 5, 6, 3, 6), board, True)
    execute((False, 6, 5), board, False)
    execute((True, 6, 6, 4, 5), board, True)
    execute((False, 4, 5), board, False)
    #probably misplay (fixed)
    execute((True, 4, 6, 6, 6), board, True)
    execute((True, 6, 6, 6, 4), board, False)
    execute((True, 6, 4, 4, 6), board, True)


    #misplay here
    # execute((True, 4, 6, 2, 6), board, True)
    # execute((True, 3, 6, 1, 5), board, False)
    # execute((True, 2, 6, 2, 4), board, True)
    # execute((True, 2, 4, 0, 4), board, False)

    printb(board)
    print(find_best_move_mp(board, 4, True))