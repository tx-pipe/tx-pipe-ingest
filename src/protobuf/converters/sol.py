from typing import Type, Dict, Any, Optional

from generated import sol_tx_pb2
from src.protobuf.base import AbstractProtoConverter
from src.rpc.models.sol_rpc_response import (
    ConfirmedTransaction, RpcResponse, UiTokenAmount, TokenBalance,
    InnerInstruction, Header, Instruction, Message, Transaction, Meta
)


class SOLProtoConverter(AbstractProtoConverter[RpcResponse]):
    def __init__(self, model: Type[RpcResponse]):
        super().__init__(model)

    def to_proto(self, rpc_response: RpcResponse):
        return self.__convert_confirmed_transaction_pb(rpc_response.result)

    def __convert_ui_token_amount_pb(self, uta: UiTokenAmount) -> sol_tx_pb2.UiTokenAmount:
        proto_uta = sol_tx_pb2.UiTokenAmount()
        proto_uta.ui_amount = uta.uiAmount if uta.uiAmount is not None else 0.0
        proto_uta.decimals = uta.decimals
        proto_uta.amount = uta.amount
        proto_uta.ui_amount_string = uta.uiAmountString
        return proto_uta

    def __convert_token_balance_pb(self, tb: TokenBalance) -> sol_tx_pb2.TokenBalance:
        proto_tb = sol_tx_pb2.TokenBalance()
        proto_tb.account_index = tb.accountIndex
        proto_tb.mint = tb.mint
        proto_tb.owner = tb.owner
        proto_tb.program_id = tb.programId
        proto_tb.ui_token_amount.CopyFrom(self.__convert_ui_token_amount_pb(tb.uiTokenAmount))
        return proto_tb

    def __convert_inner_instruction_pb(self, inst: Dict[str, Any]) -> sol_tx_pb2.InnerInstruction:
        proto_inst = sol_tx_pb2.InnerInstruction()
        proto_inst.program_id_index = inst.get("programIdIndex", 0)
        # Convert list of ints to bytes (assumes each int fits in one byte)
        proto_inst.accounts = bytes(inst.get("accounts", []))
        proto_inst.data = inst.get("data", "").encode("utf-8")
        if "stackHeight" in inst and inst["stackHeight"] is not None:
            proto_inst.stack_height = inst["stackHeight"]
        return proto_inst

    def __convert_inner_instructions_pb(self, ii: InnerInstruction) -> sol_tx_pb2.InnerInstructions:
        proto_ii = sol_tx_pb2.InnerInstructions()
        proto_ii.index = ii.index
        for inst in ii.instructions:
            proto_ii.instructions.append(self.__convert_inner_instruction_pb(inst))
        return proto_ii

    def __convert_header_pb(self, header: Header) -> sol_tx_pb2.MessageHeader:
        proto_header = sol_tx_pb2.MessageHeader()
        proto_header.num_required_signatures = header.numRequiredSignatures
        proto_header.num_readonly_signed_accounts = header.numReadonlySignedAccounts
        proto_header.num_readonly_unsigned_accounts = header.numReadonlyUnsignedAccounts
        return proto_header

    def __convert_instruction_pb(self, inst: Instruction) -> sol_tx_pb2.CompiledInstruction:
        proto_inst = sol_tx_pb2.CompiledInstruction()
        proto_inst.program_id_index = inst.programIdIndex
        proto_inst.accounts = bytes(inst.accounts)
        proto_inst.data = inst.data.encode("utf-8")
        return proto_inst

    def __convert_address_table_lookup_pb(self, lookup: dict) -> sol_tx_pb2.MessageAddressTableLookup:
        proto_lookup = sol_tx_pb2.MessageAddressTableLookup()
        proto_lookup.account_key = lookup.get("accountKey", "").encode("utf-8")
        proto_lookup.writable_indexes = bytes(lookup.get("writableIndexes", []))
        proto_lookup.readonly_indexes = bytes(lookup.get("readonlyIndexes", []))
        return proto_lookup

    def __convert_message_pb(self, msg: Message) -> sol_tx_pb2.Message:
        proto_msg = sol_tx_pb2.Message()
        proto_msg.header.CopyFrom(self.__convert_header_pb(msg.header))
        for key in msg.accountKeys:
            proto_msg.account_keys.append(key.encode("utf-8"))
        proto_msg.recent_blockhash = msg.recentBlockhash.encode("utf-8")
        for inst in msg.instructions:
            proto_msg.instructions.append(self.__convert_instruction_pb(inst))
        # Set versioned flag if address table lookups are provided
        proto_msg.versioned = bool(msg.addressTableLookups and len(msg.addressTableLookups) > 0)
        if msg.addressTableLookups:
            for lookup in msg.addressTableLookups:
                proto_msg.address_table_lookups.append(self.__convert_address_table_lookup_pb(lookup))
        return proto_msg

    def __convert_transaction_pb(self, tx: Transaction) -> sol_tx_pb2.Transaction:
        proto_tx = sol_tx_pb2.Transaction()
        for sig in tx.signatures:
            proto_tx.signatures.append(sig.encode("utf-8"))
        proto_tx.message.CopyFrom(self.__convert_message_pb(tx.message))
        return proto_tx

    def __convert_transaction_error_pb(self, err: Optional[Any]) -> sol_tx_pb2.TransactionError:
        proto_err = sol_tx_pb2.TransactionError()
        if err is not None:
            proto_err.err = str(err).encode("utf-8")
        else:
            proto_err.err = b""
        return proto_err

    def __convert_reward_pb(self, reward: dict) -> sol_tx_pb2.Reward:
        proto_reward = sol_tx_pb2.Reward()
        proto_reward.pubkey = reward.get("pubkey", "")
        proto_reward.lamports = reward.get("lamports", 0)
        proto_reward.post_balance = reward.get("post_balance", 0)
        proto_reward.reward_type = reward.get("reward_type", 0)
        proto_reward.commission = reward.get("commission", "")
        return proto_reward

    def __convert_meta_pb(self, meta: Meta) -> sol_tx_pb2.TransactionStatusMeta:
        proto_meta = sol_tx_pb2.TransactionStatusMeta()
        proto_meta.err.CopyFrom(self.__convert_transaction_error_pb(meta.err))
        proto_meta.fee = meta.fee
        proto_meta.pre_balances.extend(meta.preBalances)
        proto_meta.post_balances.extend(meta.postBalances)
        for ii in meta.innerInstructions:
            proto_meta.inner_instructions.append(self.__convert_inner_instructions_pb(ii))
        proto_meta.inner_instructions_none = (len(meta.innerInstructions) == 0)
        proto_meta.log_messages.extend(meta.logMessages)
        proto_meta.log_messages_none = (len(meta.logMessages) == 0)
        for tb in meta.preTokenBalances:
            if isinstance(tb, sol_tx_pb2.TokenBalance):
                proto_meta.pre_token_balances.append(self.__convert_token_balance_pb(tb))
        for tb in meta.postTokenBalances:
            proto_meta.post_token_balances.append(self.__convert_token_balance_pb(tb))
        for r in meta.rewards:
            proto_meta.rewards.append(self.__convert_reward_pb(r))
        writable = meta.loadedAddresses.get("writable", [])
        readonly = meta.loadedAddresses.get("readonly", [])
        for addr in writable:
            proto_meta.loaded_writable_addresses.append(addr.encode("utf-8"))
        for addr in readonly:
            proto_meta.loaded_readonly_addresses.append(addr.encode("utf-8"))
        # If no return data is provided, set as empty.
        proto_rd = sol_tx_pb2.ReturnData()
        proto_rd.program_id = b""
        proto_rd.data = b""
        proto_meta.return_data.CopyFrom(proto_rd)
        proto_meta.return_data_none = True
        proto_meta.compute_units_consumed = meta.computeUnitsConsumed
        return proto_meta

    def __convert_confirmed_transaction_pb(self, ct: ConfirmedTransaction) -> sol_tx_pb2.ConfirmedTransaction:
        proto_ct = sol_tx_pb2.ConfirmedTransaction()
        proto_ct.transaction.CopyFrom(self.__convert_transaction_pb(ct.transaction))
        proto_ct.meta.CopyFrom(self.__convert_meta_pb(ct.meta))
        return proto_ct
