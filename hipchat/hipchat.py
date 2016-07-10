#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from json import loads, dumps
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError
from urlparse import urljoin


class HipChatException(Exception):
    def __init__(self, value, code):
        self.value = value
        self.code = code

    def __str__(self):
        return repr(self.value)


class HipChat:
    def __init__(self, url, token):
        self.api_url = urljoin(url, "v2/")
        self.token = token
        self.format = "json"
        self.headers = {"Accept": "application/json", "Content-type": "application/json"}

    def __invoke_method(self, command, method="GET", parameters=None):
        if parameters is None:
            parameters = {}

        method_url = urljoin(self.api_url, command)
        request_data = None

        if method == "GET":
            parameters["format"] = self.format
            parameters["auth_token"] = self.token
            query_string = urlencode(parameters)
            method_url = method_url + "?" + query_string
        else:
            parameters["auth_token"] = self.token
            request_data = dumps(parameters)
            self.headers["Authorization"] = "Bearer {0}".format(self.token)

        req = Request(method_url, data=request_data, headers=self.headers)
        req.get_method = lambda: method

        try:
            response = urlopen(req).read()
        except HTTPError as e:
            print "{0} : {1}".format(method_url, e)
            return None

        try:
            return loads(response.decode("utf-8"))
        except ValueError:
            return response.decode("utf-8")

    def get_all_rooms(self):
        result = self.__invoke_method("room")
        if not result:
            raise HipChatException("Cannot get all rooms", 1)
        return result

    def get_room_by_id(self, room_id):
        result = self.__invoke_method("room/{0}".format(room_id))
        if not result:
            raise HipChatException("Cannot get room name by id={0}".format(room_id), 2)
        return result

    def get_room_by_name(self, room_name):
        rooms_object = self.get_all_rooms()
        for room in rooms_object["items"]:
            if room_name == room["name"]:
                return self.get_room_by_id(room["id"])
        raise HipChatException("Room {0} not found".format(room_name), 7)

    def get_room_id_by_name(self, room_name):
        rooms_object = self.get_all_rooms()
        for room in rooms_object["items"]:
            if room_name == room["name"]:
                return str(room["id"])
        raise HipChatException("Room {0} not found".format(room_name), 7)

    def create_room(self, room_name, privacy="public"):
        parameters = {"name": room_name, "privacy": privacy}
        result = self.__invoke_method("room", "POST", parameters)
        if not result:
            raise HipChatException("Cannot create room {0}".format(room_name), 3)

    def delete_room(self, room_name):
        result = self.__invoke_method("room/{0}".format(room_name), "DELETE")
        if not result:
            raise HipChatException("Cannot delete room {0}".format(room_name), 4)

    def send_message(self, room_id, message):
        parameters = {"message": message}
        result = self.__invoke_method("room/{0}/message".format(room_id), "POST", parameters)
        if not result:
            raise HipChatException("Cannot send message to room {0}".format(room_id), 5)

    def send_notification(self, room_id, sender, title, message, color):
        parameters = {"sender": sender, "title": title, "message": message, "color": color}
        result = self.__invoke_method("room/{0}/notification".format(room_id), "POST", parameters)
        if not result:
            raise HipChatException("Cannot send notification to room {0}".format(room_id), 6)
