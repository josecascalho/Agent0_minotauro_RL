#!/usr/bin/env python3
import time

from middleware import connection
from middleware import constants

def main():
    client = connection.Connection(constants.HOST, constants.PORT)
    res = client.connect()
    if res != -1:
        while True:
            command = input("Insert action value pairs:").split()
            if len(command) != 2:
                action, value = "", ""
            else:
                action, value = command
            print("Action Value pair:", action, ":", value)
            msg = client.snd_rcv_msg(action, value)
            # test
            client.print_message(msg)


if __name__ == "__main__":
    main()
