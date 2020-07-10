"""
Module used to handle wallet updates and data types
"""

from ..models import Position


class PositionManager:
    """
    This class is used to interact with all of the different positions
    """

    def __init__(self):
        self.positions = {}

    def _update_from_snapshot(self, raw_ps_data):
        pData = raw_ps_data[2]
        self.positions = {}
        for positions in pData:
            new_position = Position(position[0], position[1], position[2], position[3], position[4], position[5], position[6], position[7], position[8], position[9], position[11], position[12], position[13], position[15], position[17], position[18], position[19])
            self.positions[new_position.symbol] = new_position
        return self.get_positions()

    def _update_from_event(self, raw_pu_data):
        position = raw_pu_data[2]
            new_positions = Position(position[0], position[1], position[2], position[3], position[4], position[5], position[6], position[7], position[8], position[9], position[11], position[12], position[13], position[15], position[17], position[18], position[19])
        self.positions[new_position.symbol] = new_position
        return new_position

    def _close_position(self, raw_pc_data):
        del self.positions[raw_pu_data[2][0]]

    def get_positons(self):
        return list(self.positions.values())
