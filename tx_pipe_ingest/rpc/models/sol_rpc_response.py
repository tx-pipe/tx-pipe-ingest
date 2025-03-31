from typing import Optional, Any, List, Dict, Union
from pydantic import BaseModel


# All in one file bcause it helps when working with protobuf,
# which often have all structure in one file


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


class Header(BaseModel):
    numReadonlySignedAccounts: int
    numReadonlyUnsignedAccounts: int
    numRequiredSignatures: int


class Instruction(BaseModel):
    accounts: List[int]
    data: str
    programIdIndex: int
    stackHeight: Optional[int]


class Message(BaseModel):
    accountKeys: List[str]
    addressTableLookups: Optional[List[Any]] = None
    header: Header
    instructions: List[Instruction]
    recentBlockhash: str


class Transaction(BaseModel):
    message: Message
    signatures: List[str]


class ConfirmedTransaction(BaseModel):
    blockTime: int
    meta: Meta
    transaction: Transaction


class RpcResponse(BaseModel):
    result: ConfirmedTransaction
