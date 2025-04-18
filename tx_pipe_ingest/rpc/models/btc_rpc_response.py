from typing import Optional, List
from pydantic import BaseModel


# Keep models in one file bcause it helps when working with protobuf,
# which often have all structure in one file


class ScriptSig(BaseModel):
    asm: str
    hex: str


class ScriptPubKey(BaseModel):
    asm: str
    hex: str
    desc: Optional[str] = None
    address: Optional[str] = None
    type: str


class Vin(BaseModel):
    txid: Optional[str] = None
    vout: Optional[int] = None
    scriptSig: Optional[ScriptSig] = None
    txinwitness: Optional[List[str]] = None

    coinbase: Optional[str] = None

    sequence: int


class Vout(BaseModel):
    value: float
    n: int
    scriptPubKey: ScriptPubKey


class BTCTransaction(BaseModel):
    txid: str
    hash: str
    version: int
    size: int
    vsize: int
    weight: int
    locktime: int
    vin: List[Vin]
    vout: List[Vout]


class BTCRPCResponse(BaseModel):
    result: Optional[BTCTransaction] = None
    error: Optional[str] = None
    id: Optional[str] = None
