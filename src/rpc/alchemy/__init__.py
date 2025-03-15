import asyncio

from src.rpc.alchemy.mixins.get_tx import GetTxMixin
from src.rpc.http_client import HttpClient


class AlchemyRpcClient(
    GetTxMixin
):
    def __init__(
        self,
        http_client: HttpClient,
        alchemy_token: str,
        network: str = 'solana-mainnet'
    ):
        super().__init__(http_client, alchemy_token, network)


async def main():
    client = AlchemyRpcClient(HttpClient(), 'VCBoeKaYf6zorTm7-xmxsAxSNKl0dOqO')
    tx = await client.get_tx('5HKVZQwdsrt7AbRhztXga9ha8fLicsLTTwFjXUuAeV9VUuwxd1pLKATiKcMb7g5bhYxpze6nB1rKvdLFFt6eHPUf')
    print(tx)


if __name__ == '__main__':
    asyncio.run(main())
