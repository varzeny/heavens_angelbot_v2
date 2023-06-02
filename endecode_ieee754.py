import struct


def decode_short(list_data):
    return struct.unpack(">f",struct.pack(">HH",*list_data))[0]


def encode_short(data):
    return struct.unpack(">HH",struct.pack(">f",data))


def check_tcp(list_rg_tcp):
    return [decode_short(list_rg_tcp[i:i+2]) for i in range(0,12,2)]