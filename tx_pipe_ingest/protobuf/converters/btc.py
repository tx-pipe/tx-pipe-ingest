# Copyright (c) 2025 dffdeeq
# SPDX-License-Identifier: MIT

from typing import Type

from tx_pipe_ingest.protobuf.base import AbstractProtoConverter
from tx_pipe_ingest.rpc.models.btc_rpc_response import BTCRPCResponse as PydanticBTCRPCResponse
from tx_pipe_ingest.generated.proto.btc_raw_tx_value_pb2 import BTCMessage


class BTCProtoConverter(AbstractProtoConverter[PydanticBTCRPCResponse]):
    """
    Converts Bitcoin RPC responses from their Pydantic model representation
    to Protocol Buffer messages.
    """

    def __init__(self, model: Type[PydanticBTCRPCResponse]):
        super().__init__(model)

    def to_proto(self, response: PydanticBTCRPCResponse) -> BTCMessage:
        """
        Convert a Pydantic BTCRPCResponse to a Protocol Buffer message.

        Args:
            response: The BTC RPC response in Pydantic model form

        Returns:
            A fully populated BTCMessage Protocol Buffer message
        """
        proto_message = BTCMessage()
        proto_response = BTCMessage.Response()

        if response.result:
            proto_response.result.CopyFrom(self._convert_btc_transaction(response.result))

        if response.error:
            proto_response.error = response.error

        if response.id:
            proto_response.id = response.id

        proto_message.response.CopyFrom(proto_response)
        return proto_message

    def _convert_btc_transaction(self, tx) -> BTCMessage.BTCTransaction:
        """Convert a BTC transaction to its Protocol Buffer representation."""
        proto_tx = BTCMessage.BTCTransaction(
            txid=tx.txid,
            hash=tx.hash,
            version=tx.version,
            size=tx.size,
            vsize=tx.vsize,
            weight=tx.weight,
            locktime=tx.locktime
        )

        proto_tx.vin.extend([self._convert_vin(v) for v in tx.vin])
        proto_tx.vout.extend([self._convert_vout(v) for v in tx.vout])

        return proto_tx

    def _convert_vin(self, vin) -> BTCMessage.Vin:
        """Convert a transaction input (vin) to its Protocol Buffer representation."""
        if vin.coinbase:
            # Handle coinbase transaction (block reward)
            proto_vin = BTCMessage.Vin(
                coinbase=vin.coinbase,
                sequence=vin.sequence
            )
        else:
            # Handle regular transaction input
            proto_vin = BTCMessage.Vin(
                txid=vin.txid,
                vout=vin.vout,
                scriptSig=self._convert_script_sig(vin.scriptSig),
                sequence=vin.sequence
            )
            # Add witness data if present
            if vin.txinwitness:
                proto_vin.txinwitness.extend(vin.txinwitness)

        return proto_vin

    def _convert_vout(self, vout) -> BTCMessage.Vout:
        """Convert a transaction output (vout) to its Protocol Buffer representation."""
        return BTCMessage.Vout(
            value=vout.value,
            n=vout.n,
            scriptPubKey=self._convert_script_pubkey(vout.scriptPubKey)
        )

    @staticmethod
    def _convert_script_sig(script_sig) -> BTCMessage.ScriptSig:
        """Convert a script signature to its Protocol Buffer representation."""
        return BTCMessage.ScriptSig(
            asm=script_sig.asm,
            hex=script_sig.hex
        )

    @staticmethod
    def _convert_script_pubkey(script_pubkey) -> BTCMessage.ScriptPubKey:
        """Convert a script public key to its Protocol Buffer representation."""
        return BTCMessage.ScriptPubKey(
            asm=script_pubkey.asm,
            hex=script_pubkey.hex,
            desc=script_pubkey.desc or "",
            address=script_pubkey.address or "",
            type=script_pubkey.type
        )
