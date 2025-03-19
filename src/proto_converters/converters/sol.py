from typing import Type
from google.protobuf.struct_pb2 import Struct  # noqa
from google.protobuf.wrappers_pb2 import DoubleValue, Int32Value  # noqa

from src.proto_converters.base import AbstractProtoConverter
from generated.sol_tx_pb2 import (
    UiTokenAmount,  # noqa
    TokenBalance,  # noqa
    InnerInstruction,  # noqa
    Meta,  # noqa
    Header,  # noqa
    Instruction,  # noqa
    Message,  # noqa
    Transaction,  # noqa
    Result,  # noqa
)


class SOLProtoConverter(AbstractProtoConverter[Result]):
    def __init__(self, model: Type[Result]):
        super().__init__(model)

    def to_proto(self, result: Result):
        proto_obj = Result()
        proto_obj.blockTime = result.blockTime
        proto_obj.meta.CopyFrom(self.__convert_meta(result.meta))
        proto_obj.slot = result.slot
        proto_obj.transaction.CopyFrom(self.__convert_transaction(result.transaction))

        return proto_obj

    def __convert_ui_token_amount(self, pydantic_obj):
        proto_obj = UiTokenAmount()
        proto_obj.amount = pydantic_obj.amount
        proto_obj.decimals = pydantic_obj.decimals
        if pydantic_obj.uiAmount is not None:
            proto_obj.uiAmount.CopyFrom(DoubleValue(value=pydantic_obj.uiAmount))
        proto_obj.uiAmountString = pydantic_obj.uiAmountString
        return proto_obj

    def __convert_token_balance(self, pydantic_obj):
        proto_obj = TokenBalance()
        proto_obj.accountIndex = pydantic_obj.accountIndex
        proto_obj.mint = pydantic_obj.mint
        proto_obj.owner = pydantic_obj.owner
        proto_obj.programId = pydantic_obj.programId
        proto_obj.uiTokenAmount.CopyFrom(self.__convert_ui_token_amount(pydantic_obj.uiTokenAmount))
        return proto_obj

    def __convert_inner_instruction(self, pydantic_obj):
        proto_obj = InnerInstruction()
        proto_obj.index = pydantic_obj.index
        for instruction_dict in pydantic_obj.instructions:
            struct_inst = Struct()
            struct_inst.update(instruction_dict)
            proto_obj.instructions.append(struct_inst)
        return proto_obj

    def __convert_meta(self, pydantic_obj):
        proto_obj = Meta()
        proto_obj.computeUnitsConsumed = pydantic_obj.computeUnitsConsumed
        if pydantic_obj.err is not None:
            proto_obj.err.CopyFrom(self._convert_to_value(pydantic_obj.err))
        proto_obj.fee = pydantic_obj.fee
        for inner_inst in pydantic_obj.innerInstructions:
            proto_obj.innerInstructions.append(self.__convert_inner_instruction(inner_inst))
        for key, value_list in pydantic_obj.loadedAddresses.items():
            proto_obj.loadedAddresses[key].values.extend(value_list)
        proto_obj.logMessages.extend(pydantic_obj.logMessages)
        proto_obj.postBalances.extend(pydantic_obj.postBalances)
        for tb in pydantic_obj.postTokenBalances:
            proto_obj.postTokenBalances.append(self.__convert_token_balance(tb))
        proto_obj.preBalances.extend(pydantic_obj.preBalances)
        for pt in pydantic_obj.preTokenBalances:
            proto_obj.preTokenBalances.append(self._convert_to_value(pt))
        for r in pydantic_obj.rewards:
            proto_obj.rewards.append(self._convert_to_value(r))
        for key, value in pydantic_obj.status.items():
            proto_obj.status[key].CopyFrom(self._convert_to_value(value))
        return proto_obj

    def __convert_header(self, pydantic_obj):
        proto_obj = Header()
        proto_obj.numReadonlySignedAccounts = pydantic_obj.numReadonlySignedAccounts
        proto_obj.numReadonlyUnsignedAccounts = pydantic_obj.numReadonlyUnsignedAccounts
        proto_obj.numRequiredSignatures = pydantic_obj.numRequiredSignatures
        return proto_obj

    def __convert_instruction(self, pydantic_obj):
        proto_obj = Instruction()
        proto_obj.accounts.extend(pydantic_obj.accounts)
        proto_obj.data = pydantic_obj.data
        proto_obj.programIdIndex = pydantic_obj.programIdIndex
        if pydantic_obj.stackHeight is not None:
            proto_obj.stackHeight.CopyFrom(Int32Value(value=pydantic_obj.stackHeight))
        return proto_obj

    def __convert_message(self, pydantic_obj):
        proto_obj = Message()
        proto_obj.accountKeys.extend(pydantic_obj.accountKeys)
        if pydantic_obj.addressTableLookups is not None:
            for lookup in pydantic_obj.addressTableLookups:
                proto_obj.addressTableLookups.append(self._convert_to_value(lookup))
        proto_obj.header.CopyFrom(self.__convert_header(pydantic_obj.header))
        for instr in pydantic_obj.instructions:
            proto_obj.instructions.append(self.__convert_instruction(instr))
        proto_obj.recentBlockhash = pydantic_obj.recentBlockhash
        return proto_obj

    def __convert_transaction(self, pydantic_obj):
        proto_obj = Transaction()
        proto_obj.message.CopyFrom(self.__convert_message(pydantic_obj.message))
        proto_obj.signatures.extend(pydantic_obj.signatures)
        return proto_obj
