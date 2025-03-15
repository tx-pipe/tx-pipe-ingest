from typing import List, Any, Optional, Dict

from pydantic import BaseModel


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
