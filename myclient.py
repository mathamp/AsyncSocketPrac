import asyncio
import struct
import secrets
import sys
import time

host = "localhost"
port = 8765


def generate_mask_key() -> bytes:
    return secrets.token_bytes(4)


def apply_mask(data: bytes, mask_key: bytes) -> bytes:
    assert len(mask_key) == 4, "Mask key should be 4 bytes"
    data_int = int.from_bytes(data, sys.byteorder)
    n, mod = divmod(len(data), 4)
    mask_repeated = mask_key * n + mask_key[: mod]
    mask_int = int.from_bytes(mask_repeated, sys.byteorder)
    return (data_int ^ mask_int).to_bytes(len(data), sys.byteorder)


OPCODE_TEXT = 0b0001
OPCODE_CLOSE = 0b1000

HEADER_MASK = HEADER_FIN = 0b10000000


def frame(opcode: int, message: bytes, mask_key: bytes) -> bytes:
    return (
        struct.pack("!BB", HEADER_FIN | opcode, HEADER_MASK | len(message))
        + mask_key
        + apply_mask(message, mask_key)
    )


CLOSE_NORMAL = 1000


def frame_close(status_code: int, message: bytes, mask_key: bytes):
    return frame(OPCODE_CLOSE, struct.pack("!H", status_code) + message, mask_key)


def frame_message(message: bytes, mask_key: bytes):
    return frame(OPCODE_TEXT, message, mask_key)


async def main():
    t = time.perf_counter()
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(b"GET / HTTP/1.1\r\n"
                 b"Host: localhost:8765\r\n"
                 b"Upgrade: websocket\r\n"
                 b"Connection: Upgrade\r\n"
                 b"Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==\r\n"
                 b"Sec-WebSocket-Version: 13\r\n\r\n")
    await writer.drain()

    data = await reader.read(1 << 15)
    print(data)

    writer.write(frame_message(b"hi are you? I'm Good!", generate_mask_key()))
    await writer.drain()

    writer.write(frame_close(1000, "GoodBye".encode("UTF-8"), generate_mask_key()))
    await writer.drain()

    print(await reader.read(1 << 15))

    writer.close()

    print(time.perf_counter() - t)


if __name__ == "__main__":
    asyncio.run(main())
