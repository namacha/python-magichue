import socket


def make_socket(timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    return sock


def discover_bulbs(timeout=1, broadcast_ip="255.255.255.255"):
    DISCOVERY_PORT = 48899
    DISCOVERY_MSG = b"HF-A11ASSISTHREAD"
    addrs = []

    sock = make_socket(timeout)
    sock.sendto(DISCOVERY_MSG, (broadcast_ip, DISCOVERY_PORT))

    try:
        while True:
            response, addr = sock.recvfrom(64)
            if response != DISCOVERY_MSG:
                addr = response.decode().split(",")[0]
                addrs.append(addr)
    except socket.timeout:
        pass

    sock.close()
    return addrs
