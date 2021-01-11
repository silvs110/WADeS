import copy
from pprint import pprint
from typing import Tuple, Any, Union, KeysView, ValuesView, ItemsView, Dict, Iterator

import idna


class RangeKeyDict:

    def __init__(self) -> None:
        """
        Creates an instance of a dictionary with range as keys.
        """
        self.__range_key_dict = dict()

    def __getitem__(self, key: Union[float, int, Tuple[Union[float, int], Union[float, int]]]) -> Any:
        """
        Retrieves the value associated to the provided key.
        :param key: The key used to retrieve the value.
        :type key: Union[float, int, Tuple[Union[float, int], Union[float, int]]]
        :return: The value associated to the key provided.
        :rtype: Any
        """
        for found_key, value in self.__range_key_dict.items():
            if (isinstance(key, tuple) and key == found_key) or (
                    isinstance(key, (int, float)) and self.key(key) == found_key):
                return value
        return None

    def __setitem__(self, key: Union[float, int, Tuple[Union[float, int], Union[float, int]]], value: Any) -> None:
        """
        Sets the new value of the key.
        :param key: The key to set the new value.
        :type key: Union[float, int, Tuple[Union[float, int], Union[float, int]]]
        :param value: the new value of the key.
        :type value: Any
        :raises ValueError: if the second value of key is less than the first value,
                        or if the items in the tuple are not of the same type.
        """
        assert isinstance(key, (tuple, int, float))
        if isinstance(key, tuple):
            if not isinstance(key[0], type(key[1])):
                raise ValueError("Items in tuple should both be of the same type.")
            if key[0] > key[1]:
                raise ValueError("Second item in key tuple should be larger than first item.")

            self.__range_key_dict[key] = value

        else:
            key_found = self.key(key)
            if key_found is None:
                # noinspection PyArgumentList
                key_found = (value, value + 1)
            self.__range_key_dict[key_found] = value

    def keys(self) -> KeysView:
        """
        Gets the keys of the dictionary.
        :return: the keys of the dictionary.
        :rtype: KeysView
        """
        return self.__range_key_dict.keys()

    def values(self) -> ValuesView:
        """
        Gets the values of the dictionary.
        :return: the values of the dictionary.
        :rtype: ValuesView
        """
        return self.__range_key_dict.values()

    def key(self, key_item: Union[float, int]) -> Union[None, Tuple[Union[float, int], Union[float, int]]]:
        """
        Gets the key as tuple from the provided key (float, int). Finds the range the key_item belongs to.
        :param key_item: the key to find the range for.
        :type key_item: Union[float, int]
        :return: The range of the key_item belongs to. It returns None if the key does not belong in any key range.
        :rtype: Union[None, Tuple[Union[float, int], Union[float, int]]]
        """
        assert isinstance(key_item, (float, int))

        for key, value in self.__range_key_dict.items():
            if key[0] <= key_item < key[1]:
                return key
        return None

    def items(self) -> ItemsView:
        """
        Gets the items of the dictionary.
        :return: the items of the dictionary.
        :rtype: ItemsView
        """
        return self.__range_key_dict.items()

    def __repr__(self) -> str:
        """
        Gets the representation of the dictionary as a string.
        :return: The representation of the dictionary as a string.
        :rtype: str
        """
        return repr(self.__range_key_dict)

    def __len__(self) -> int:
        """
        Gets the number of keys in the dictionary.
        :return: The number of keys in the dictionary.
        :rtype: int
        """
        return len(self.__range_key_dict)

    def __delitem__(self, key: Union[float, int, Tuple[Union[float, int], Union[float, int]]]) -> None:
        """
        Deletes the key from the dictionary.
        :param key: The key to delete.
        :type key: Union[float, int, Tuple[Union[float, int], Union[float, int]]]
        """
        del self.__range_key_dict[self.key(key)]

    def clear(self) -> None:
        """
        Clears the dictionary.
        """
        return self.__range_key_dict.clear()

    def copy(self) -> Dict[Union[int, float, Tuple[Union[int, float], Union[int, float]]], Any]:
        """
        Gets a deep copy of the dictionary.
        :return: A deep copy of the dictionary.
        :rtype: Dict[Union[int, float, Tuple[Union[int, float], Union[int, float]]], Any]
        """
        return copy.deepcopy(self.__range_key_dict)

    def has_key(self, key: Union[float, int, Tuple[Union[float, int], Union[float, int]]]) -> bool:
        """
        Checks that the dictionary contains a certain key.
        :param key: The key to check.
        :type key: Union[float, int, Tuple[Union[float, int], Union[float, int]]]
        :return: True if the key is found, False otherwise.
        :rtype: bool
        """
        return self.__contains__(key)

    def pop(self, *keys: Union[float, int, Tuple[Union[float, int], Union[float, int]]]) -> None:
        """
        Pops the keys from the dictionary.
        :param keys: The keys to pop.
        :type keys: Union[float, int, Tuple[Union[float, int], Union[float, int]]]
        """
        keys_to_pop = set()
        for key in keys:
            if key is not None and self.key(key) is not None:
                keys_to_pop.add(self.key(key))

        self.__range_key_dict.pop(keys_to_pop)

    def __contains__(self, key: Union[float, int, Tuple[Union[float, int], Union[float, int]]]) -> bool:
        """
        Checks that the dictionary contains a certain key.
        :param key: The key to check.
        :type key: Union[float, int, Tuple[Union[float, int], Union[float, int]]]
        :return: True if the key is found, False otherwise.
        :rtype: bool
        """
        return key in self.__range_key_dict or (isinstance(key, (int, float)) and self.key(key) is not None)

    def __iter__(self) -> Iterator:
        """
        Gets an iterator from the dictionary.
        :return: An iterator from the dictionary.
        :rtype: Iterator
        """
        return iter(self.__range_key_dict)

    def __unicode__(self) -> str:
        """
        Gets the unicode of the string representation of the dictionary.
        :return: The unicode of the string representation of the dictionary.
        :rtype: str
        """
        return idna.unicode(repr(self.__range_key_dict))


if __name__ == '__main__':
    range_dict = RangeKeyDict()
    range_dict[1, 9] = 1200
    range_dict[9] = 3
    print(range_dict[9])

    pprint(range_dict)
