from typing import Type

from src.proto_converters.base import AbstractProtoConverter
from src.rpc.models.btc_rpc_response import BTCRPCResponse
from generated.btc_tx_pb2 import (
    BTCRPCResponse,  # noqa
    BTCTransaction,  # noqa
    Vin,  # noqa
    Vout,  # noqa
    ScriptSig,  # noqa
    ScriptPubKey # noqa
)

class BTCProtoConverter(AbstractProtoConverter[BTCRPCResponse]):
    def __init__(self, model: Type[BTCRPCResponse]):
        super().__init__(model)

    def __convert_script_sig(self, script_sig) -> ScriptSig:
        return ScriptSig(
            asm=script_sig.asm,
            hex=script_sig.hex
        )

    def __convert_script_pubkey(self, script_pubkey) -> ScriptPubKey:
        return ScriptPubKey(
            asm=script_pubkey.asm,
            hex=script_pubkey.hex,
            desc=script_pubkey.desc or "",
            address=script_pubkey.address or "",
            type=script_pubkey.type
        )

    def __convert_vin(self, vin) -> Vin:
        proto_vin = Vin(
            txid=vin.txid,
            vout=vin.vout,
            scriptSig=self.__convert_script_sig(vin.scriptSig),
            sequence=vin.sequence
        )

        if vin.txinwitness:
            proto_vin.txinwitness.extend(vin.txinwitness)

        if vin.coinbase:
            proto_vin.coinbase = vin.coinbase

        return proto_vin

    def __convert_vout(self, vout) -> Vout:
        return Vout(
            value=vout.value,
            n=vout.n,
            scriptPubKey=self.__convert_script_pubkey(vout.scriptPubKey)
        )

    def __convert_btc_transaction(self, tx) -> BTCTransaction:
        proto_tx = BTCTransaction(
            txid=tx.txid,
            hash=tx.hash,
            version=tx.version,
            size=tx.size,
            vsize=tx.vsize,
            weight=tx.weight,
            locktime=tx.locktime
        )

        proto_tx.vin.extend([self.__convert_vin(v) for v in tx.vin])
        proto_tx.vout.extend([self.__convert_vout(v) for v in tx.vout])

        return proto_tx

    def convert_rpc_response(self, response: BTCRPCResponse) -> BTCRPCResponse:
        proto_response = BTCRPCResponse()

        if response.result:
            proto_response.result.CopyFrom(self.__convert_btc_transaction(response.result))

        if response.error:
            proto_response.error = response.error

        if response.id:
            proto_response.id = response.id

        return proto_response
