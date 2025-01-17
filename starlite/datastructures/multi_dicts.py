from abc import ABC
from typing import (
    Any,
    Dict,
    Generator,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
)
from urllib.parse import parse_qsl

from multidict import MultiDict as BaseMultiDict
from multidict import MultiDictProxy, MultiMapping

from starlite.datastructures.upload_file import UploadFile
from starlite.utils import deprecated

T = TypeVar("T")


class MultiMixin(Generic[T], MultiMapping[T], ABC):
    """Mixin providing common methods for multi dicts, used by.

    [ImmutableMultiDict][starlite.datastructures.multi_dicts.ImmutableMultiDict] and
    [MultiDict][starlite.datastructures.multi_dicts.MultiDict]
    """

    def dict(self) -> Dict[str, List[Any]]:
        """

        Returns:
            A dict of lists
        """
        return {k: self.getall(k) for k in set(self.keys())}

    def multi_items(self) -> Generator[Tuple[str, T], None, None]:
        """Get all keys and values, including duplicates.

        Returns:
            A list of tuples containing key-value pairs
        """
        for key in set(self):
            for value in self.getall(key):
                yield key, value

    @deprecated("1.36.0", alternative="FormMultiDict.getall")
    def getlist(self, key: str) -> List[T]:
        """Get all values.

        Args:
            key: The key

        Returns:
            A list of values
        """
        return super().getall(key, [])


class MultiDict(BaseMultiDict[T], MultiMixin[T], Generic[T]):
    def __init__(self, args: Optional[Union["MultiMapping", Mapping[str, T], Iterable[Tuple[str, T]]]] = None) -> None:
        super().__init__(args or {})

    def immutable(self) -> "ImmutableMultiDict[T]":
        """Create an.

        [ImmutableMultiDict][starlite.datastructures.multi_dicts.ImmutableMultiDict] view.

        Returns:
            An immutable multi dict
        """
        return ImmutableMultiDict[T](self)


class ImmutableMultiDict(MultiDictProxy[T], MultiMixin[T], Generic[T]):
    def __init__(
        self, args: Optional[Union["MultiMapping", Mapping[str, Any], Iterable[Tuple[str, Any]]]] = None
    ) -> None:
        super().__init__(BaseMultiDict(args or {}))

    def mutable_copy(self) -> MultiDict[T]:
        """Create a mutable copy as a.

        [MultiDict][starlite.datastructures.multi_dicts.MultiDict]

        Returns:
            A mutable multi dict
        """
        return MultiDict(list(self.multi_items()))


class FormMultiDict(ImmutableMultiDict[Any]):
    async def close(self) -> None:
        """Closes all files in the multi-dict.

        Returns:
            None
        """
        for _, value in self.multi_items():
            if isinstance(value, UploadFile):
                await value.close()


class QueryMultiDict(MultiDict):
    @classmethod
    def from_query_string(cls, query_string: str) -> "QueryMultiDict":
        """Creates a QueryMultiDict from a query string.

        Args:
            query_string: A query string.

        Returns:
            A QueryMultiDict instance
        """
        _bools = {"true": True, "false": False, "True": True, "False": False}
        return cls(
            (k, v) if v not in _bools else (k, _bools[v]) for k, v in parse_qsl(query_string, keep_blank_values=True)
        )
