# Copyright (c) 2025 dffdeeq
# SPDX-License-Identifier: MIT

from typing import Type, Dict, Any

from tx_pipe_ingest.protobuf.base import AbstractProtoConverter
from tx_pipe_ingest.rpc.models.sol_rpc_response import SOLRPCResponse, TokenBalance, UiTokenAmount
from tx_pipe_ingest.generated.proto.sol_raw_tx_value_pb2 import ConfirmedTransaction


class SOLProtoConverter(AbstractProtoConverter[SOLRPCResponse]):
    """
    Converts Solana RPC responses from their Pydantic model representation
    to Protocol Buffer messages.
    """

    def __init__(self, model: Type[SOLRPCResponse]):
        super().__init__(model)

    def to_proto(self, response: SOLRPCResponse) -> ConfirmedTransaction:
        """
        Convert a Pydantic Solana RPC Response to a Protocol Buffer message.

        Args:
            response: The Solana RPC response in Pydantic model form

        Returns:
            A fully populated ConfirmedTransaction Protocol Buffer message
        """
        if not response.result:
            return ConfirmedTransaction()

        return self._convert_confirmed_transaction(response.result)

    def _convert_confirmed_transaction(self, ct) -> ConfirmedTransaction:
        """Convert a confirmed transaction to its Protocol Buffer representation."""
        proto_ct = ConfirmedTransaction()
        proto_ct.transaction.CopyFrom(self._convert_transaction(ct.transaction))
        proto_ct.meta.CopyFrom(self._convert_meta(ct.meta))
        return proto_ct

    def _convert_transaction(self, tx) -> ConfirmedTransaction.Transaction:
        """Convert a transaction to its Protocol Buffer representation."""
        proto_tx = ConfirmedTransaction.Transaction()

        # Convert signatures to UTF-8 encoded bytes
        for sig in tx.signatures:
            proto_tx.signatures.append(sig.encode("utf-8"))

        proto_tx.message.CopyFrom(self._convert_message(tx.message))
        return proto_tx

    def _convert_message(self, msg) -> ConfirmedTransaction.Message:
        """Convert a transaction message to its Protocol Buffer representation."""
        proto_msg = ConfirmedTransaction.Message()

        # Convert header
        proto_msg.header.CopyFrom(self._convert_header(msg.header))

        # Convert account keys to UTF-8 encoded bytes
        for key in msg.accountKeys:
            proto_msg.account_keys.append(key.encode("utf-8"))

        proto_msg.recent_blockhash = msg.recentBlockhash.encode("utf-8")

        # Convert instructions
        for inst in msg.instructions:
            proto_msg.instructions.append(self._convert_instruction(inst))

        # Handle address table lookups for versioned transactions
        has_lookups = bool(msg.addressTableLookups and len(msg.addressTableLookups) > 0)
        proto_msg.versioned = has_lookups

        if has_lookups:
            for lookup in msg.addressTableLookups:
                proto_msg.address_table_lookups.append(
                    self._convert_address_table_lookup(lookup)
                )

        return proto_msg

    def _convert_meta(self, meta) -> ConfirmedTransaction.TransactionStatusMeta:
        """Convert transaction metadata to its Protocol Buffer representation."""
        proto_meta = ConfirmedTransaction.TransactionStatusMeta()

        # Convert error information
        proto_meta.err.CopyFrom(self._convert_transaction_error(meta.err))

        # Set fee and balance information
        proto_meta.fee = meta.fee
        proto_meta.pre_balances.extend(meta.preBalances)
        proto_meta.post_balances.extend(meta.postBalances)

        # Convert inner instructions
        for ii in meta.innerInstructions:
            proto_meta.inner_instructions.append(self._convert_inner_instructions(ii))
        proto_meta.inner_instructions_none = (len(meta.innerInstructions) == 0)

        # Set log messages
        proto_meta.log_messages.extend(meta.logMessages)
        proto_meta.log_messages_none = (len(meta.logMessages) == 0)

        # Convert token balances - handle both pydantic models and dictionaries
        for tb in meta.preTokenBalances:
            proto_meta.pre_token_balances.append(self._convert_token_balance_any(tb))

        for tb in meta.postTokenBalances:
            proto_meta.post_token_balances.append(self._convert_token_balance_any(tb))

        # Convert rewards
        for r in meta.rewards:
            proto_meta.rewards.append(self._convert_reward(r))

        # Handle loaded addresses
        writable = meta.loadedAddresses.get("writable", [])
        readonly = meta.loadedAddresses.get("readonly", [])

        for addr in writable:
            proto_meta.loaded_writable_addresses.append(addr.encode("utf-8"))

        for addr in readonly:
            proto_meta.loaded_readonly_addresses.append(addr.encode("utf-8"))

        # Handle return data (always set as empty for now)
        proto_rd = ConfirmedTransaction.ReturnData()
        proto_rd.program_id = b""
        proto_rd.data = b""
        proto_meta.return_data.CopyFrom(proto_rd)
        proto_meta.return_data_none = True

        # Set compute units information
        proto_meta.compute_units_consumed = meta.computeUnitsConsumed

        return proto_meta

    def _convert_token_balance_any(self, tb_data: Any) -> ConfirmedTransaction.TokenBalance:
        """
        Convert a token balance from any format (dict or Pydantic) to Protocol Buffer.
        """
        proto_tb = ConfirmedTransaction.TokenBalance()

        # Handle dictionary input
        if isinstance(tb_data, dict):
            proto_tb.account_index = tb_data.get("accountIndex", 0)
            proto_tb.mint = tb_data.get("mint", "")
            proto_tb.owner = tb_data.get("owner", "")
            proto_tb.program_id = tb_data.get("programId", "")

            ui_token_amount = tb_data.get("uiTokenAmount", {})
            proto_tb.ui_token_amount.CopyFrom(self._convert_ui_token_amount_dict(ui_token_amount))

        # Handle Pydantic model input
        elif isinstance(tb_data, TokenBalance):
            proto_tb.account_index = tb_data.accountIndex
            proto_tb.mint = tb_data.mint
            proto_tb.owner = tb_data.owner
            proto_tb.program_id = tb_data.programId
            proto_tb.ui_token_amount.CopyFrom(self._convert_ui_token_amount(tb_data.uiTokenAmount))

        return proto_tb

    def _convert_inner_instructions(self, ii) -> ConfirmedTransaction.InnerInstructions:
        """Convert inner instructions to their Protocol Buffer representation."""
        proto_ii = ConfirmedTransaction.InnerInstructions()
        proto_ii.index = ii.index
        for inst in ii.instructions:
            proto_ii.instructions.append(self._convert_inner_instruction(inst))
        return proto_ii

    def _convert_ui_token_amount(self, uta: UiTokenAmount) -> ConfirmedTransaction.UiTokenAmount:
        """Convert a UI token amount Pydantic model to its Protocol Buffer representation."""
        return ConfirmedTransaction.UiTokenAmount(
            ui_amount=uta.uiAmount if uta.uiAmount is not None else 0.0,
            decimals=uta.decimals,
            amount=uta.amount,
            ui_amount_string=uta.uiAmountString
        )

    def _convert_ui_token_amount_dict(self, uta: Dict) -> ConfirmedTransaction.UiTokenAmount:
        """Convert a UI token amount dictionary to its Protocol Buffer representation."""
        return ConfirmedTransaction.UiTokenAmount(
            ui_amount=uta.get("uiAmount", 0.0),
            decimals=uta.get("decimals", 0),
            amount=uta.get("amount", "0"),
            ui_amount_string=uta.get("uiAmountString", "0")
        )

    @staticmethod
    def _convert_inner_instruction(inst: Dict) -> ConfirmedTransaction.InnerInstruction:
        """Convert an inner instruction dictionary to its Protocol Buffer representation."""
        proto_inst = ConfirmedTransaction.InnerInstruction()
        proto_inst.program_id_index = inst.get("programIdIndex", 0)
        proto_inst.accounts = bytes(inst.get("accounts", []))
        proto_inst.data = inst.get("data", "").encode("utf-8")

        if "stackHeight" in inst and inst["stackHeight"] is not None:
            proto_inst.stack_height = inst["stackHeight"]

        return proto_inst

    @staticmethod
    def _convert_header(header) -> ConfirmedTransaction.MessageHeader:
        """Convert a message header to its Protocol Buffer representation."""
        return ConfirmedTransaction.MessageHeader(
            num_required_signatures=header.numRequiredSignatures,
            num_readonly_signed_accounts=header.numReadonlySignedAccounts,
            num_readonly_unsigned_accounts=header.numReadonlyUnsignedAccounts
        )

    @staticmethod
    def _convert_instruction(inst) -> ConfirmedTransaction.CompiledInstruction:
        """Convert a compiled instruction to its Protocol Buffer representation."""
        return ConfirmedTransaction.CompiledInstruction(
            program_id_index=inst.programIdIndex,
            accounts=bytes(inst.accounts),
            data=inst.data.encode("utf-8")
        )

    @staticmethod
    def _convert_address_table_lookup(lookup) -> ConfirmedTransaction.MessageAddressTableLookup:
        """Convert an address table lookup to its Protocol Buffer representation."""
        if isinstance(lookup, dict):
            return ConfirmedTransaction.MessageAddressTableLookup(
                account_key=lookup.get("accountKey", "").encode("utf-8"),
                writable_indexes=bytes(lookup.get("writableIndexes", [])),
                readonly_indexes=bytes(lookup.get("readonlyIndexes", []))
            )
        else:
            # Handle if it's a Pydantic model
            return ConfirmedTransaction.MessageAddressTableLookup(
                account_key=getattr(lookup, "accountKey", "").encode("utf-8"),
                writable_indexes=bytes(getattr(lookup, "writableIndexes", [])),
                readonly_indexes=bytes(getattr(lookup, "readonlyIndexes", []))
            )

    @staticmethod
    def _convert_transaction_error(err) -> ConfirmedTransaction.TransactionError:
        """Convert a transaction error to its Protocol Buffer representation."""
        proto_err = ConfirmedTransaction.TransactionError()
        if err is not None:
            proto_err.err = str(err).encode("utf-8")
        else:
            proto_err.err = b""
        return proto_err

    @staticmethod
    def _convert_reward(reward) -> ConfirmedTransaction.Reward:
        """Convert a reward to its Protocol Buffer representation."""
        if isinstance(reward, dict):
            # Map string reward types to enum values if needed
            reward_type = reward.get("reward_type", 0)
            if isinstance(reward_type, str):
                reward_type_map = {
                    "unspecified": 0,
                    "fee": 1,
                    "rent": 2,
                    "staking": 3,
                    "voting": 4
                }
                reward_type = reward_type_map.get(reward_type.lower(), 0)

            return ConfirmedTransaction.Reward(
                pubkey=reward.get("pubkey", ""),
                lamports=reward.get("lamports", 0),
                post_balance=reward.get("post_balance", 0),
                reward_type=reward_type,
                commission=reward.get("commission", "")
            )
        else:
            # Handle if it's not a dictionary
            return ConfirmedTransaction.Reward(
                pubkey=getattr(reward, "pubkey", ""),
                lamports=getattr(reward, "lamports", 0),
                post_balance=getattr(reward, "post_balance", 0),
                reward_type=getattr(reward, "reward_type", 0),
                commission=getattr(reward, "commission", "")
            )
