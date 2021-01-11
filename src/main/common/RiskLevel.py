from enum import Enum, IntEnum


class RiskLevel(IntEnum):
    none = 1
    low = 2
    medium = 3
    high = 4

    def __add__(self, level: int) -> 'RiskLevel':
        assert isinstance(level, int)
        new_level = self.value + level
        # noinspection PyProtectedMember
        if new_level not in RiskLevel._value2member_map_:
            new_level = self.value
        return RiskLevel(new_level)

    def __sub__(self, level: int) -> 'RiskLevel':
        assert isinstance(level, int)
        new_level = self.value - level
        # noinspection PyProtectedMember
        if new_level not in RiskLevel._value2member_map_:
            new_level = self.value
        return RiskLevel(new_level)


if __name__ == '__main__':
    enums = {e for e in RiskLevel}
    print(max(enums))
