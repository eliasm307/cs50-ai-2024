"""
Tic Tac Toe Player
"""

from copy import deepcopy
from typing import List, Literal, TypedDict

X = "X"
O = "O"
EMPTY = None

RowColumn = tuple[int, int]
XO = Literal["X"] | Literal["O"]
Board = List[List[XO | None]]


def initial_state() -> Board:
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board: Board) -> XO:
    """
    Returns player who has the next turn on a board.
    """
    x_count = 0
    o_count = 0
    for row in board:
        for cell in row:
            if cell == X:
                x_count += 1
            elif cell == O:
                o_count += 1

    if x_count == o_count:
        return X  # X goes first

    return O


def actions(board: Board) -> set[RowColumn]:
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    output: set[RowColumn] = set()
    for row_index, row in enumerate(board):
        for column_index, cell in enumerate(row):
            if not cell:
                output.add((row_index, column_index))

    return output


def result(board: Board, action: RowColumn):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    max_row_index = len(board) - 1
    max_column_index = len(board[0]) - 1
    if action[0] < 0 or action[0] > max_row_index or action[1] < 0 or action[1] > max_column_index:
        raise Exception("Action coordinates are invalid")

    if board[action[0]][action[1]]:
        raise Exception("Action coordinates already taken")

    output = deepcopy(board)
    output[action[0]][action[1]] = player(board)
    return output


def get_winning_value(values: List[XO | None]) -> XO | None:
    unique_values = list(set(values))
    if len(unique_values) == 1 and unique_values[0]:
        return unique_values[0]


def winner(board: Board) -> XO | None:
    """
    Returns the winner of the game, if there is one.
    """

    # check for winning rows ie those that only contain the same value for all columns
    for row in board:
        winning_value = get_winning_value(row)
        if winning_value:
            return winning_value

    # check for winning columns ie those that only contain the same value for all rows
    # NOTE: calculating counts so the algorithm is generic and can work for different board sizes
    row_count = len(board)
    column_count = len(board[0])
    for column_index in range(column_count):
        # get values in the current column
        column: list[XO | None] = []
        for row_index in range(row_count):
            column.append(board[row_index][column_index])

        # check if it is a winning column
        winning_value = get_winning_value(column)
        if winning_value:
            return winning_value

    # check for winning forward diagonal
    column_index = 0  # start from top left
    diagonal: list[XO | None] = []
    for row_index in range(row_count):
        diagonal.append(board[row_index][column_index])
        column_index += 1

    # check if it is a winning diagonal
    winning_value = get_winning_value(diagonal)
    if winning_value:
        return winning_value

    # check for winning backward diagonal
    column_index = column_count - 1  # start from top right
    diagonal = []
    for row_index in range(row_count):
        diagonal.append(board[row_index][column_index])
        column_index -= 1

    # check if it is a winning diagonal
    winning_value = get_winning_value(diagonal)
    if winning_value:
        return winning_value

    # no winner found
    return None


def terminal(board: Board):
    """
    Returns True if game is over, False otherwise.
    """

    # check if someone won
    if winner(board):
        return True

    # check if there are no more possible actions
    return len(actions(board)) == 0


def utility(board: Board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winning_player = winner(board)
    if winning_player == X:
        return 1

    elif winning_player == O:
        return -1

    return 0


def get_board_key(board: Board) -> str:
    return str(board)


class Move(TypedDict):
    score: float
    action: RowColumn | None


# the score only depends on the board state so we can cache the results
# NOTE: key is generated from the board state
board_max_score_cache: dict[str, Move] = {}
board_min_score_cache: dict[str, Move] = {}

MAX_SCORE = 1
MIN_SCORE = -1


def get_best_move(board: Board, is_minimising: bool) -> Move:
    # check if we have already calculated the score for this board
    cache = board_min_score_cache if is_minimising else board_max_score_cache
    key = get_board_key(board)
    if key in cache:
        return cache[key]

    if terminal(board):
        # game is over return result
        cache[key] = {
            "score": utility(board),
            "action": None
        }
        return cache[key]

    # default to worst score
    best: Move = {
        "score": MAX_SCORE if is_minimising else MIN_SCORE,
        "action": None
    }

    limit = MIN_SCORE if is_minimising else MAX_SCORE

    for action in actions(board):
        next = get_best_move(result(board, action), not is_minimising)
        score_is_lower = next['score'] < best['score']
        if is_minimising == score_is_lower:
            best = {
                "score": next['score'],
                "action": action
            }

        if best['score'] == limit:
            break  # cant get any better

    cache[key] = best
    return cache[key]


def minimax(board: Board) -> RowColumn | None:
    """
    Returns the optimal action for the current player on the board.
    """

    best = get_best_move(
        board=board,
        is_minimising=player(board) == O
    )

    return best['action']

