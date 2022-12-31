import socket
import asyncio

import myclient

HOST = socket.gethostbyname(socket.gethostname())


def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    s.bind((HOST, 0))

    # Include IP headers
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # receive all packets
    s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    return s


async def main():
    asyncio.create_task(myclient.main())

    loop = asyncio.get_running_loop()
    s = create_socket()

    while True:
        bs = await loop.sock_recv(s, 1 << 16)
        print(len(bs))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Keyboard Interrupted")
