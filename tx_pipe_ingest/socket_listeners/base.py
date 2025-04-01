from abc import abstractmethod, ABC
from typing import Callable, Any, Awaitable, TypeVar, Generic

from pydantic_settings import BaseSettings


T = TypeVar('T', bound=BaseSettings)


class AbstractSocketListener(ABC, Generic[T]):
    def __init__(self, settings: T):
        self.settings = settings

    @abstractmethod
    async def subscribe(self, on_event: Callable[[Any, Any], Awaitable[Any]], *args, **kwargs) -> None:
        """Subscribe to socket events"""
        pass
