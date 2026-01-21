"""
This is a bare-bones implementation, some things may be incorrect.
"""

import io
import enum


"""
The maximum length of a pkt-line’s data component is 65520 bytes. Implementations MUST NOT 
send pkt-line whose length exceeds 65524 (65520 bytes of payload + 4 bytes of length data).

Implementations SHOULD NOT send an empty pkt-line ("0004").

A pkt-line with a length field of 0 ("0000"), called a flush-pkt, is a special case and MUST 
be handled differently than an empty pkt-line ("0004").
"""
PKT_MAX_SIZE = 65520


class SidebandChannel(enum.IntEnum):
    Data = 1
    Progress = 2
    Error = 3


def write_message(ch: SidebandChannel, data: bytes) -> bytes:
    return int.to_bytes(ch) + bytes(data, "utf-8")


def write_pktline(data: bytes) -> bytes:
    if type(data) == str:
        data = bytes(data, "utf-8")

    datalen = len(data)
    assert 0 < datalen <= PKT_MAX_SIZE, f"0 < {datalen} <= {PKT_MAX_SIZE}"

    return bytes(int.to_bytes(datalen + 4, 2, "big").hex(), "ascii") + data


def parse_pktline(buffer: io.BytesIO) -> bytes:
    message_len_str = buffer.read(4)
    if message_len_str == b"0001":
        return b"\n"

    message_len_int = int(message_len_str, 16)
    if message_len_int > 0:
        return buffer.read(message_len_int - 4)

    return b""


def decode_buffer(buffer: bytes):
    """
    protocol-version = PKT-LINE("version 2" LF)
    capability-list = *capability
    capability = PKT-LINE(key[=value] LF)

    https://github.com/git/git/blob/master/Documentation/gitprotocol-v2.adoc#capabilities
    """
    messages = []

    buf = io.BytesIO(buffer)
    while buf.tell() < len(buf.getbuffer()):
        m = parse_pktline(buf)
        messages.append(m)

    return messages


def create_advertisement() -> bytes:
    buffer = b""
    buffer += write_pktline("# service=git-upload-pack\n")
    buffer += b"0000"
    buffer += write_pktline("version 2\n")
    buffer += write_pktline("agent=git-cinema\n")
    buffer += write_pktline("ls-refs=unborn\n")
    buffer += write_pktline("fetch=shallow\n")
    buffer += write_pktline("server-option\n")
    buffer += write_pktline("object-format=sha1\n")
    buffer += b"0000"
    return buffer


def create_ref_list() -> bytes:
    buffer = b""
    buffer += write_pktline(
        "6861686168616861686168616861686168616861 HEAD symref-target:refs/heads/hahaha\n"
    )
    buffer += write_pktline(
        "6861686168616861686168616861686168616861 refs/heads/hahaha\n"
    )
    buffer += b"0000"

    return buffer
