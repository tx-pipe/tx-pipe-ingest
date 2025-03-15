from typing import Optional, Any, List, Dict, Union

from google.protobuf.json_format import ParseDict
from pydantic import BaseModel

import tx_pb2
from src.rpc.alchemy.models.tx import Transaction


class UiTokenAmount(BaseModel):
    amount: str
    decimals: int
    uiAmount: Optional[float]
    uiAmountString: str


class TokenBalance(BaseModel):
    accountIndex: int
    mint: str
    owner: str
    programId: str
    uiTokenAmount: UiTokenAmount


class InnerInstruction(BaseModel):
    index: int
    instructions: List[Dict[str, Any]]


class Meta(BaseModel):
    computeUnitsConsumed: int
    err: Optional[Any]
    fee: int
    innerInstructions: List[InnerInstruction]
    loadedAddresses: Dict[str, List[str]]
    logMessages: List[str]
    postBalances: List[int]
    postTokenBalances: List[TokenBalance]
    preBalances: List[int]
    preTokenBalances: List[Any]
    rewards: List[Any]
    status: Dict[str, Optional[Any]]


class Result(BaseModel):
    blockTime: int
    meta: Meta
    slot: int
    transaction: Transaction
    version: Union[int, str]


class RpcResponse(BaseModel):
    jsonrpc: str
    result: Result
    id: int
