import json
from enum import Enum, IntEnum


class RiskLevel(IntEnum):
    none = 1
    low = 2
    medium = 3
    high = 4

    def __add__(self, level: int) -> 'RiskLevel':
        """
        Overloads adding two Risk levels.
        :param level: The level to add.
        :type level: int
        :return: The result of the sum.
        :rtype: RiskLevel
        """
        assert isinstance(level, int)
        new_level = self.value + level
        # noinspection PyProtectedMember
        if new_level not in RiskLevel._value2member_map_:
            new_level = self.value
        return RiskLevel(new_level)

    def __sub__(self, level: int) -> 'RiskLevel':
        """
        Overloads subtracting two Risk levels.
        :param level: The level to substract.
        :type level: int
        :return: The result of the substraction.
        :rtype: RiskLevel
        """
        assert isinstance(level, int)
        new_level = self.value - level
        # noinspection PyProtectedMember
        if new_level not in RiskLevel._value2member_map_:
            new_level = self.value
        return RiskLevel(new_level)