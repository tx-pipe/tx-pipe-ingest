from abc import abstractmethod, ABC
from typing import TypeVar, Generic, Type

from google.protobuf import struct_pb2
from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class AbstractProtoConverter(ABC, Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    @abstractmethod
    def to_proto(self, val: T):
        pass

    def _convert_to_value(self, val):
        value_pb = struct_pb2.Value()
        if val is None:
            value_pb.null_value = struct_pb2.NullValue.NULL_VALUE
        elif isinstance(val, bool):
            value_pb.bool_value = val
        elif isinstance(val, (int, float)):
            value_pb.number_value = val
        elif isinstance(val, str):
            value_pb.string_value = val
        elif isinstance(val, list):
            list_val = struct_pb2.ListValue()
            for item in val:
                sub_val = list_val.values.add()
                sub_val.CopyFrom(self._convert_to_value(item))
            value_pb.list_value.CopyFrom(list_val)
        elif isinstance(val, dict):
            struct_val = struct_pb2.Struct()
            for k, v in val.items():
                struct_val.fields[k].CopyFrom(self._convert_to_value(v))
            value_pb.struct_value.CopyFrom(struct_val)
        else:
            value_pb.string_value = str(val)
        return value_pb
