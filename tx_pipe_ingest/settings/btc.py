from pydantic_settings import BaseSettings


class BTCSettings(BaseSettings):
    zmq_tcp_address: str
    zmq_stream_type: str  # e.g. 'rawtx'
    rpc_user: str
    rpc_password: str
    rpc_url: str
