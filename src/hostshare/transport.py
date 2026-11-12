"""Host-only reference model. No MMIO, DMA, QNX interrupts or native driver."""
from dataclasses import dataclass
import struct

VERSION_1 = 1 << 32
MOUNT_TAG = 1

@dataclass(frozen=True)
class Region:
    bar: int
    offset: int
    length: int
    notify_multiplier: int = 0

def capabilities(config: bytes, bars: dict[int, int]) -> dict[int, Region]:
    if len(config) != 256 or not struct.unpack_from('<H', config, 6)[0] & 0x10:
        raise ValueError('PCI capability list unavailable')
    at, seen, result = config[0x34], set(), {}
    while at:
        if at < 0x40 or at > 0xfc or at % 4 or at in seen:
            raise ValueError('invalid or cyclic PCI capability chain')
        seen.add(at)
        ident, nxt = config[at:at+2]
        if ident == 9:
            size, kind = config[at+2:at+4]
            if size < 16 or at + size > len(config):
                raise ValueError('truncated vendor capability')
            if kind in (1, 2, 3, 4):
                if kind in result:
                    raise ValueError('duplicate required capability')
                bar = config[at+4]
                offset, length = struct.unpack_from('<II', config, at+8)
                if bar not in bars or bar > 5 or not length or offset + length > bars[bar]:
                    raise ValueError('BAR region outside supplied mapping')
                if kind == 2 and size < 20:
                    raise ValueError('notify multiplier missing')
                minimum = {1:56, 2:2, 3:1, 4:2}[kind]
                if length < minimum:
                    raise ValueError('required region too short')
                result[kind] = Region(bar, offset, length, struct.unpack_from('<I', config, at+16)[0] if kind == 2 else 0)
        at = nxt
    if set(result) != {1, 2, 3, 4}:
        raise ValueError('missing modern virtio regions')
    return result

def negotiate(offered: int) -> int:
    required = VERSION_1 | MOUNT_TAG
    if offered & required != required:
        raise ValueError('VERSION_1 and MOUNT_TAG required')
    return required

def mount_tag(device_config: bytes) -> str:
    if len(device_config) < 2:
        raise ValueError('missing tag length')
    length = struct.unpack_from('<H', device_config)[0]
    if not 0 < length <= 255 or length + 2 > len(device_config):
        raise ValueError('invalid mount tag length')
    tag = device_config[2:2+length].decode('utf-8', errors='strict')
    if chr(0) in tag:
        raise ValueError('NUL mount tag')
    return tag

class OneQueue:
    """One outstanding request; synthetic completion and pulse callback only.

    Callback is the future IRQ-to-QNX-pulse boundary, NOT an implementation of
    InterruptAttachEvent, DMA barriers, descriptor rings or MMIO notification.
    """
    def __init__(self, size: int, pulse):
        if not 2 <= size <= 32768 or size & (size-1):
            raise ValueError('queue size must be power of two')
        self.size, self.pulse, self.pending, self.sequence = size, pulse, None, 0
    def submit(self, request: bytes, response_limit: int) -> int:
        if self.pending is not None:
            raise RuntimeError('queue busy')
        if not request or not 7 <= response_limit <= 1048576:
            raise ValueError('invalid descriptor bounds')
        token = self.sequence
        self.sequence = (self.sequence + 1) & 0xffff
        self.pending = (token, bytes(request), response_limit)
        return token
    def complete(self, token: int, response: bytes) -> bytes:
        if self.pending is None or token != self.pending[0]:
            raise ValueError('unexpected used descriptor')
        if len(response) > self.pending[2]:
            raise ValueError('used length exceeds writable descriptor')
        self.pending = None
        result = bytes(response)
        self.pulse(token)
        return result
