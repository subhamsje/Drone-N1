"""
WebSocket streaming layer — pure asyncio, no external dependencies.
Implements RFC 6455 WebSocket server (text frames only).
"""

import asyncio
import hashlib
import base64
import struct
import json
import logging
from collections import deque
from typing import Set, List

from core.models import SystemSnapshot
from config.settings import SystemConfig

logger = logging.getLogger("streamer")

_WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _make_accept(key: str) -> str:
    combined = (key.strip() + _WS_MAGIC).encode()
    return base64.b64encode(hashlib.sha1(combined).digest()).decode()


def _encode_frame(data: str) -> bytes:
    payload = data.encode("utf-8")
    n = len(payload)
    if n < 126:
        header = struct.pack("BB", 0x81, n)
    elif n < 65536:
        header = struct.pack("!BBH", 0x81, 126, n)
    else:
        header = struct.pack("!BBQ", 0x81, 127, n)
    return header + payload


class _WSClient:
    def __init__(self, writer: asyncio.StreamWriter):
        self.writer = writer
        self.alive = True

    async def send(self, text: str):
        if not self.alive:
            return
        try:
            self.writer.write(_encode_frame(text))
            await self.writer.drain()
        except Exception:
            self.alive = False


class StreamingLayer:
    def __init__(self, config: SystemConfig):
        cfg = config.stream
        self._host = cfg.websocket_host
        self._port = cfg.websocket_port
        self._path = cfg.json_output_path
        self._buffer: deque = deque(maxlen=cfg.buffer_size)
        self._clients: Set[_WSClient] = set()
        self._server = None

    async def start_websocket_server(self):
        try:
            self._server = await asyncio.start_server(
                self._handle_connection, self._host, self._port
            )
            logger.info(f"[Streamer] WS server at ws://{self._host}:{self._port}")
        except Exception as e:
            logger.warning(f"[Streamer] Could not start WS server: {e}")

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        client = None
        try:
            raw = b""
            while b"\r\n\r\n" not in raw:
                chunk = await asyncio.wait_for(reader.read(4096), timeout=5.0)
                if not chunk:
                    return
                raw += chunk

            headers = {}
            for line in raw.decode("utf-8", errors="replace").split("\r\n")[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    headers[k.strip().lower()] = v.strip()

            ws_key = headers.get("sec-websocket-key", "")
            if not ws_key:
                return

            accept = _make_accept(ws_key)
            writer.write((
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept}\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "\r\n"
            ).encode())
            await writer.drain()

            client = _WSClient(writer)
            self._clients.add(client)

            for msg in self._buffer:
                await client.send(msg)

            while client.alive:
                try:
                    data = await asyncio.wait_for(reader.read(4096), timeout=30.0)
                    if not data:
                        break
                    if len(data) >= 2:
                        opcode = data[0] & 0x0F
                        if opcode == 0x8:
                            break
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    break
        except Exception as e:
            logger.debug(f"[Streamer] Client error: {e}")
        finally:
            if client:
                client.alive = False
                self._clients.discard(client)
            try:
                writer.close()
            except Exception:
                pass

    async def emit(self, snap: SystemSnapshot):
        data = json.dumps(snap.to_dict())
        self._buffer.append(data)
        try:
            with open(self._path, "a") as f:
                f.write(data + "\n")
        except Exception:
            pass
        dead = set()
        for client in list(self._clients):
            await client.send(data)
            if not client.alive:
                dead.add(client)
        self._clients -= dead

    def get_recent(self, n: int = 10) -> List[str]:
        return list(self._buffer)[-n:]
