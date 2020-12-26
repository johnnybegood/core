"""Base component for Lares"""
import logging

import asyncio
import aiohttp
from aiohttp.http import RESPONSES

from lxml import etree

_LOGGER = logging.getLogger(__name__)


class LaresBase:
    """The implementation of the Lares base class."""

    def __init__(self, host: str, username: str, password: str):
        self._auth = aiohttp.BasicAuth(username, password)
        self._host = f"http://{host}:4202"

    async def ping(self):
        """Test connection"""
        return True

    async def info(self):
        """Get device info"""
        response = await self.get("info/generalInfo.xml")
        _LOGGER.info(response)

        if response is None:
            return None

        info = {
            "name": response.xpath("/generalInfo/productName")[0].text,
            "info": response.xpath("/generalInfo/info1")[0].text,
        }

        return info

    async def get(self, path):
        """Generic send method."""
        url = f"{self._host}/xml/{path}"

        try:
            async with aiohttp.ClientSession(auth=self._auth) as session:
                async with session.get(url=url) as response:
                    xml = await response.read()
                    content = etree.fromstring(xml)
                    return content

        except aiohttp.ClientConnectorError as conn_err:
            _LOGGER.debug("Host %s: Connection error %s", self._host, str(conn_err))
        except:  # pylint: disable=bare-except
            _LOGGER.debug("Host %s: Unknown exception occurred.", self._host)
        return