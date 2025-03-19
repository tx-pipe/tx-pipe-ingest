from typing import Dict
from pydantic import Field

from src.settings.factory import SettingsFactory


class BTCSettings(SettingsFactory):
    zmq_tcp: str = Field(description='ZMQ TCP address')
    zmq_stream_type: str = Field(description='ZMQ stream type (e.g. rawtx)', default='rawtx')
    rpc_user: str = Field()
    rpc_password: str = Field()
    rpc_url: str = Field()

    @classmethod
    def from_dict(cls, settings_dict: Dict[str, str]) -> 'BTCSettings':
        return BTCSettings(
            zmq_tcp=settings_dict.get('BTC_SETTINGS_ZMQ_TCP'),
            zmq_stream_type=settings_dict.get('BTC_SETTINGS_ZMQ_STREAM_TYPE'),
            rpc_user=settings_dict.get('BTC_SETTINGS_RPC_USER'),
            rpc_password=settings_dict.get('BTC_SETTINGS_RPC_PASSWORD'),
            rpc_url=settings_dict.get('BTC_SETTINGS_RPC_URL'),
        )
