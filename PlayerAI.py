import numpy as np
import random
import time
import sys
import os 
from BaseAI import BaseAI
from Grid import Grid

# TO BE IMPLEMENTED
# 
class PlayerAI(BaseAI):

    def __init__(self) -> None:
        # You may choose to add attributes to your player - up to you!
        super().__init__()
        self.pos = None
        self.player_num = None
        self.depth = 4
    
    def getPosition(self):
        return self.pos

    def setPosition(self, new_position):
        self.pos = new_position 

    def getPlayerNum(self):
        return self.player_num

    def setPlayerNum(self, num):
        self.player_num = num

    def getMove(self, grid: Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player moves.

        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Trap* actions, 
        taking into account the probabilities of them landing in the positions you believe they'd throw to.

        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
        max_score = float("-inf")
        max_move = None

        for possible_move in grid.get_neighbors(self.pos, only_available=True):
            min_value = self._min_value(self._simulate_move(possible_move, self.player_num, grid), self.depth, "getMove")
            if min_value > max_score:
                max_score = min_value
                max_move = possible_move

        return max_move

    def getTrap(self, grid : Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player *WANTS* to throw the trap.
        
        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Move* actions, 
        taking into account the probabilities of it landing in the positions you want. 
        
        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
        max_score = float("-inf")
        max_trap = None
        opponent_pos = grid.find(self.getOpponentNum())

        for possible_trap in grid.get_neighbors(opponent_pos, only_available=True):
            min_value = self._min_value(self._simulate_trap(possible_trap, grid), self.depth, "getTrap")
            if min_value > max_score:
                max_score = min_value
                max_trap = possible_trap

        return max_trap

    def getOpponentNum(self):
        return 1 if self.player_num == 2 else 2

    def _simulate_move(self, pos, player, grid):
        grid_clone = grid.clone()
        grid_clone.move(pos, player)

        return grid_clone

    def _simulate_trap(self, pos, grid):
        grid_clone = grid.clone()
        grid_clone.trap(pos)

        return grid_clone

    def _terminal_state(self, grid, depth):
        # Restrict depth of tree search
        if depth == 0:
            return True

        # Player is out of moves
        opponent_num = self.getOpponentNum()
        opponent_pos = grid.find(opponent_num)

        if not grid.get_neighbors(opponent_pos, only_available=True) or not grid.get_neighbors(self.pos, only_available=True):
            return True

        return False

    def _min_value(self, grid, depth, action):
        if self._terminal_state(grid, depth):
            return self._get_score(grid)

        opponent_num = self.getOpponentNum()
        opponent_pos = grid.find(opponent_num)
        player_pos = grid.find(self.player_num)
        score = float("inf")

        if action == "getTrap":
            for possible_move in grid.get_neighbors(opponent_pos, only_available=True):
                max_value = self._max_value(self._simulate_move(possible_move, opponent_num, grid), depth - 1, action)
                score = min(score, max_value)
        elif action == "getMove":
            for possible_trap in grid.get_neighbors(player_pos, only_available=True):
                max_value = self._max_value(self._simulate_trap(possible_trap, grid), depth - 1, action)
                score = min(score, max_value)

        return score

    def _max_value(self, grid, depth, action):
        if self._terminal_state(grid, depth):
            return self._get_score(grid)

        opponent_num = self.getOpponentNum()
        opponent_pos = grid.find(opponent_num)
        player_pos = grid.find(self.player_num)
        score = float("-inf")

        if action == "getTrap":
            for possible_trap in grid.get_neighbors(opponent_pos, only_available=True):
                min_value = self._min_value(self._simulate_trap(possible_trap, grid), depth - 1, action)
                score = max(score, min_value)
        elif action == "getMove":
            for possible_move in grid.get_neighbors(player_pos, only_available=True):
                min_value = self._min_value(self._simulate_move(possible_move, self.player_num, grid), depth - 1, action)
                score = max(score, min_value)

        return score

    def _get_score(self, grid):
        opponent_pos = grid.find(self.getOpponentNum())
        player_moves = len(grid.get_neighbors(self.pos, only_available=True))
        opponent_moves = len(grid.get_neighbors(opponent_pos, only_available=True))

        return float(player_moves - 2 * opponent_moves)