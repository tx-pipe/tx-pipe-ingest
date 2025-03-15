import tx_pb2
import google.protobuf.struct_pb2 as struct_pb2
import google.protobuf.wrappers_pb2 as wrappers_pb2


def convert_to_value(val):
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
            sub_val.CopyFrom(convert_to_value(item))
        value_pb.list_value.CopyFrom(list_val)
    elif isinstance(val, dict):
        struct_val = struct_pb2.Struct()
        for k, v in val.items():
            struct_val.fields[k].CopyFrom(convert_to_value(v))
        value_pb.struct_value.CopyFrom(struct_val)
    else:
        value_pb.string_value = str(val)
    return value_pb

def convert_ui_token_amount(pydantic_obj):
    proto_obj = tx_pb2.UiTokenAmount()
    proto_obj.amount = pydantic_obj.amount
    proto_obj.decimals = pydantic_obj.decimals
    if pydantic_obj.uiAmount is not None:
        proto_obj.uiAmount.CopyFrom(wrappers_pb2.DoubleValue(value=pydantic_obj.uiAmount))
    proto_obj.uiAmountString = pydantic_obj.uiAmountString
    return proto_obj

def convert_token_balance(pydantic_obj):
    proto_obj = tx_pb2.TokenBalance()
    proto_obj.accountIndex = pydantic_obj.accountIndex
    proto_obj.mint = pydantic_obj.mint
    proto_obj.owner = pydantic_obj.owner
    proto_obj.programId = pydantic_obj.programId
    proto_obj.uiTokenAmount.CopyFrom(convert_ui_token_amount(pydantic_obj.uiTokenAmount))
    return proto_obj

def convert_inner_instruction(pydantic_obj):
    proto_obj = tx_pb2.InnerInstruction()
    proto_obj.index = pydantic_obj.index
    for instruction_dict in pydantic_obj.instructions:
        struct_inst = struct_pb2.Struct()
        struct_inst.update(instruction_dict)
        proto_obj.instructions.append(struct_inst)
    return proto_obj

def convert_meta(pydantic_obj):
    proto_obj = tx_pb2.Meta()
    proto_obj.computeUnitsConsumed = pydantic_obj.computeUnitsConsumed
    if pydantic_obj.err is not None:
        proto_obj.err.CopyFrom(convert_to_value(pydantic_obj.err))
    proto_obj.fee = pydantic_obj.fee
    for inner_inst in pydantic_obj.innerInstructions:
        proto_obj.innerInstructions.append(convert_inner_instruction(inner_inst))
    for key, value_list in pydantic_obj.loadedAddresses.items():
        proto_obj.loadedAddresses[key].values.extend(value_list)
    proto_obj.logMessages.extend(pydantic_obj.logMessages)
    proto_obj.postBalances.extend(pydantic_obj.postBalances)
    for tb in pydantic_obj.postTokenBalances:
        proto_obj.postTokenBalances.append(convert_token_balance(tb))
    proto_obj.preBalances.extend(pydantic_obj.preBalances)
    for pt in pydantic_obj.preTokenBalances:
        proto_obj.preTokenBalances.append(convert_to_value(pt))
    for r in pydantic_obj.rewards:
        proto_obj.rewards.append(convert_to_value(r))
    for key, value in pydantic_obj.status.items():
        proto_obj.status[key].CopyFrom(convert_to_value(value))
    return proto_obj

def convert_header(pydantic_obj):
    proto_obj = tx_pb2.Header()
    proto_obj.numReadonlySignedAccounts = pydantic_obj.numReadonlySignedAccounts
    proto_obj.numReadonlyUnsignedAccounts = pydantic_obj.numReadonlyUnsignedAccounts
    proto_obj.numRequiredSignatures = pydantic_obj.numRequiredSignatures
    return proto_obj

def convert_instruction(pydantic_obj):
    proto_obj = tx_pb2.Instruction()
    proto_obj.accounts.extend(pydantic_obj.accounts)
    proto_obj.data = pydantic_obj.data
    proto_obj.programIdIndex = pydantic_obj.programIdIndex
    if pydantic_obj.stackHeight is not None:
        proto_obj.stackHeight.CopyFrom(wrappers_pb2.Int32Value(value=pydantic_obj.stackHeight))
    return proto_obj

def convert_message(pydantic_obj):
    proto_obj = tx_pb2.Message()
    proto_obj.accountKeys.extend(pydantic_obj.accountKeys)
    if pydantic_obj.addressTableLookups is not None:
        for lookup in pydantic_obj.addressTableLookups:
            proto_obj.addressTableLookups.append(convert_to_value(lookup))
    proto_obj.header.CopyFrom(convert_header(pydantic_obj.header))
    for instr in pydantic_obj.instructions:
        proto_obj.instructions.append(convert_instruction(instr))
    proto_obj.recentBlockhash = pydantic_obj.recentBlockhash
    return proto_obj

def convert_transaction(pydantic_obj):
    proto_obj = tx_pb2.Transaction()
    proto_obj.message.CopyFrom(convert_message(pydantic_obj.message))
    proto_obj.signatures.extend(pydantic_obj.signatures)
    return proto_obj

def pydantic_to_proto_result(pydantic_obj):
    proto_obj = tx_pb2.Result()
    proto_obj.blockTime = pydantic_obj.blockTime
    proto_obj.meta.CopyFrom(convert_meta(pydantic_obj.meta))
    proto_obj.slot = pydantic_obj.slot
    proto_obj.transaction.CopyFrom(convert_transaction(pydantic_obj.transaction))
    if isinstance(pydantic_obj.version, int):
        proto_obj.int_version = pydantic_obj.version
    else:
        proto_obj.string_version = pydantic_obj.version
    return proto_obj
