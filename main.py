# Copyright (c) 2025 dffdeeq
# SPDX-License-Identifier: MIT

import argparse
import asyncio
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    parser = argparse.ArgumentParser(description="Start TxPipe for provided blockchain")
    parser.add_argument("blockchain", help="'Blockchain name'", type=str, choices=['btc', 'sol'])
    args = parser.parse_args()

    if args.blockchain == 'sol':
        from tx_pipe_ingest.startup.sol import main
        asyncio.run(main())

    elif args.blockchain == 'btc':
        from tx_pipe_ingest.startup.btc import main
        asyncio.run(main())


if __name__ == '__main__':
    main()
