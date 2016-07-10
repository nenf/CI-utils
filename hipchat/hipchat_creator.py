#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from hipchat import HipChat, HipChatException
from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser(description="Script for create room on HipChat. Script uses config.py")
    args = parser.parse_args()
    from config import *
    print "[*] : Hipchat - creating room"
    hipchat = HipChat(HIPCHAT_SERVER, HIPCHAT_TOKEN)

    try:
        hipchat.create_room(HIPCHAT_ROOM_NAME)
    except HipChatException as e:
        print "Error: {0}, return code: {1}".format(e.value, e.code)

    room_url = "{0}/rooms/tokens/{1}".format(HIPCHAT_SERVER, hipchat.get_room_id_by_name(HIPCHAT_ROOM_NAME))
    print "Room '{0}' was created".format(HIPCHAT_ROOM_NAME)
    print "Now, you can generate notify token: {0}".format(room_url)
