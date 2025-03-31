from abc import abstractmethod, ABC
from typing import TypeVar, Generic, Type

from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class AbstractProtoConverter(ABC, Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    @abstractmethod
    def to_proto(self, val: T):
        pass
