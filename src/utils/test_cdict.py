import pytest

from utils import CDict


class TestCDict:
    @pytest.mark.parametrize('keys, expected', [
        (['a'], 1),
        (['b', 'c'], 2),
        (['b', 'd', 'e', 'a', 'whatever'], None),
    ])
    def test_get(self, keys: list[str], expected):
        d = {
            'a': 1,
            'b': {
                'c': 2
            }
        }

        value = CDict(d)

        for key in keys:
            value = value[key]

        assert value == expected
