import aiohttp
import dataclasses
import json
import logging

from json import JSONDecodeError
from typing import Any, Dict, Optional, Union, List
from urllib.parse import unquote
from aiohttp import ClientConnectorError, ContentTypeError
from starlette import status


logger = logging.getLogger(__name__)


class HttpClientException(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg


@dataclasses.dataclass
class HttpClientResponse:
    body: Dict[str, Any]
    status: int


class HttpClient:
    async def get(
        self, url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> HttpClientResponse:
        pass

    async def request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> HttpClientResponse:
        logger.info(f'Request. Url: {url}')
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.request(method, url, data=data, json=json_, params=params) as response:
                    if response.status >= status.HTTP_400_BAD_REQUEST:
                        content = await response.content.read()
                        error_msg = self._try_fetch_error_msg(content)
                        if error_msg is None:
                            logger.info(f'Failed to get error message from external service. Url: {url}')
                        raise HttpClientException(
                            f'Error when accessing external service. Url: {url}, error: {error_msg}'
                        )
                    content_type = response.headers.get('Content-Type')
                    try:
                        if content_type == 'text/plain':
                            resp_text = await response.text()
                            if resp_text:
                                try:
                                    resp_json = json.loads(resp_text)
                                    body = self._decode_json(resp_json)
                                except json.JSONDecodeError:
                                    body = resp_text
                            else:
                                body = None
                        elif content_type.find('application/json') != -1:
                            body = await response.json()
                    except ContentTypeError as exc:
                        raise HttpClientException(msg=f'Content type error. Url: {url}, exc: \n{exc}')
                    return HttpClientResponse(body=body, status=response.status)
        except ClientConnectorError as exc:
            msg = f'Failed to send request. Url: {url}, Exc: {exc}'
            logger.error(msg)
            raise HttpClientException(msg)

    @staticmethod
    def _try_fetch_error_msg(content: bytes) -> Optional[Any]:
        try:
            error_content = json.loads(content.decode('utf-8'))
            error_msg = (
                error_content.get('detail')
                or error_content.get('message')
                or error_content.get('error')
                or error_content
            )
            return error_msg
        except (UnicodeError, JSONDecodeError):
            return None

    @staticmethod
    def _decode_json(data: Union[List, Dict[str, Any]]) -> Dict[str, Any]:
        data_dumps = json.dumps(data, ensure_ascii=False)
        decoded_data_str = unquote(data_dumps)
        data_data_json = json.loads(decoded_data_str)
        return data_data_json
