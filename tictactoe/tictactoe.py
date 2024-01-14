"""
Tic Tac Toe Player
"""

from ast import Dict
from copy import deepcopy
from math import inf, isfinite
from tkinter.tix import MAX
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


def actions(board: Board) -> List[RowColumn]:
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    output: List[RowColumn] = []
    for rowIndex, row in enumerate(board):
        for column_index, cell in enumerate(row):
            if not cell:
                output.append((rowIndex, column_index))

    return output


def result(board: Board, action: RowColumn):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    output = deepcopy(board)
    # NOTE: this will implicitly error if action coordinates are invalid
    output[action[0]][action[1]] = player(board)
    return output


def get_winning_value(values: List[XO | None]) -> XO | None:
    uniqueValues = list(set(values))
    if len(uniqueValues) == 1 and uniqueValues[0]:
        return uniqueValues[0]


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
        for rowIndex in range(row_count):
            column.append(board[rowIndex][column_index])

        # check if it is a winning column
        winning_value = get_winning_value(column)
        if winning_value:
            return winning_value

    # check for winning forward diagonal
    column_index = 0  # start from top left
    diagonal: list[XO | None] = []
    for rowIndex in range(row_count):
        diagonal.append(board[rowIndex][column_index])
        column_index += 1

    # check if it is a winning diagonal
    winning_value = get_winning_value(diagonal)
    if winning_value:
        return winning_value

    # check for winning backward diagonal
    column_index = column_count - 1  # start from top right
    diagonal = []
    for rowIndex in range(row_count):
        diagonal.append(board[rowIndex][column_index])
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


MAX_SCORE = 1
MIN_SCORE = -1


class Move(TypedDict):
    score: float
    action: RowColumn | None


# the score only depends on the board state so we can cache the results
# NOTE: key is generated from the board state
board_max_score_cache: dict[str, Move] = {}
board_min_score_cache: dict[str, Move] = {}


def get_best_move(board: Board, isMinimising: bool) -> Move:
    # check if we have already calculated the score for this board
    cache = board_min_score_cache if isMinimising else board_max_score_cache
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
    best: Move  = {
        "score": MAX_SCORE if isMinimising else MIN_SCORE,
        "action": None
    }

    limit = MIN_SCORE if isMinimising else MAX_SCORE

    for action in actions(board):
        next = get_best_move(result(board, action), not isMinimising)
        if isMinimising and next['score'] < best['score']:
            best = {
                "score": next['score'],
                "action": action
            }

        elif not isMinimising and next['score'] > best['score']:
            best = {
                "score": next['score'],
                "action": action
            }

        if best['score'] == limit:
            break # cant get any better

    cache[key] = best
    return cache[key]


def minimax(board: Board) -> RowColumn | None:
    """
    Returns the optimal action for the current player on the board.
    """

    best = get_best_move(
        board=board,
        isMinimising=player(board) == O
    )

    return best['action']

