from typing import Type

from src.protobuf.base import AbstractProtoConverter
from src.rpc.models.btc_rpc_response import BTCRPCResponse as PydanticBTCRPCResponse
from generated.btc_tx_pb2 import BTCMessage  # noqa


class BTCProtoConverter(AbstractProtoConverter[PydanticBTCRPCResponse]):
    def __init__(self, model: Type[PydanticBTCRPCResponse]):
        super().__init__(model)

    def to_proto(self, response: PydanticBTCRPCResponse) -> BTCMessage:
        proto_message = BTCMessage()
        proto_response = BTCMessage.Response()

        if response.result:
            proto_response.result.CopyFrom(self.__convert_btc_transaction(response.result))

        if response.error:
            proto_response.error = response.error

        if response.id:
            proto_response.id = response.id

        proto_message.response.CopyFrom(proto_response)
        return proto_message

    def __convert_vin(self, vin) -> BTCMessage.Vin:
        if vin.coinbase:
            proto_vin = BTCMessage.Vin(
                coinbase=vin.coinbase,
                sequence=vin.sequence
            )
        else:
            proto_vin = BTCMessage.Vin(
                txid=vin.txid,
                vout=vin.vout,
                scriptSig=self.__convert_script_sig(vin.scriptSig),
                sequence=vin.sequence
            )
            if vin.txinwitness:
                proto_vin.txinwitness.extend(vin.txinwitness)
        return proto_vin

    def __convert_vout(self, vout) -> BTCMessage.Vout:
        return BTCMessage.Vout(
            value=vout.value,
            n=vout.n,
            scriptPubKey=self.__convert_script_pubkey(vout.scriptPubKey)
        )

    def __convert_btc_transaction(self, tx) -> BTCMessage.BTCTransaction:
        proto_tx = BTCMessage.BTCTransaction(
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

    @staticmethod
    def __convert_script_sig(script_sig) -> BTCMessage.ScriptSig:
        return BTCMessage.ScriptSig(
            asm=script_sig.asm,
            hex=script_sig.hex
        )

    @staticmethod
    def __convert_script_pubkey(script_pubkey) -> BTCMessage.ScriptPubKey:
        return BTCMessage.ScriptPubKey(
            asm=script_pubkey.asm,
            hex=script_pubkey.hex,
            desc=script_pubkey.desc or "",
            address=script_pubkey.address or "",
            type=script_pubkey.type
        )
