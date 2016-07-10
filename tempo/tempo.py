#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from urllib2 import Request, urlopen, HTTPError
from datetime import datetime
from urllib import urlencode
from getpass import getpass
from json import loads


class JiraException(Exception):
    def __init__(self, value, code):
        self.value = value
        self.code = code

    def __str__(self):
        return repr(self.value)


class TempoRecord:
    def __init__(self, jira_url, username, password):
        self.__rest_api = "{0}/rest/api/2/".format(jira_url)
        self.__rest_api_tempo = "{0}/rest/tempo-rest/1.0/".format(jira_url)
        self.__authentication(username, password)

    def __authentication(self, username, password):
        if not username:
            username = raw_input("Username: ").lower()
        if not password:
            password = getpass("Password: ")

        while True:
            try:
                user_data = "Basic " + (username + ":" + password).encode("base64").rstrip()
                self.headers = {"Accept": "application/json", "Content-type": "application/json",
                                 "Authorization": user_data}
                self.headers_tempo = {"Authorization": user_data,
                                       "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
                self.check_permissions()
            except JiraException as e:
                print e
                try:
                    username = raw_input("Username: ").lower()
                    password = getpass("Password: ")
                except KeyboardInterrupt:
                    print "\n"
                    exit(0)
            else:
                return True

    def __invoke_method_jira(self, method):
        req = Request(self.__rest_api + method, headers=self.headers)

        try:
            result = loads(urlopen(req).read())
        except HTTPError as e:
            print "Invoke {0} failed: {1} (return code {2})".format(method, e.msg, e.code)
            return None
        except Exception as e:
            print "Some error: {0}".format(e.message)
            return None

        return result

    def __invoke_method_tempo(self, method, data):
        if data:
            data = urlencode(data)
        else:
            data = ""
        url = self.__rest_api_tempo + method
        req = Request(url, data, headers=self.headers_tempo)

        try:
            result = urlopen(req).read()
        except HTTPError as e:
            print "Invoke {0} failed: {1} (return code {2})".format(method, e.msg, e.code)
            return None
        except Exception as e:
            print "Some error: {0}".format(e.message)
            return None

        return result

    def worklog(self, issue_id, user_name, user_date, time_spent):
        """
        :param issue_id: like TEST-1
        :param user_name: User name
        :param user_date: format like 11.03.16
        :param time_spent: 1h 30m;
        :return: Result in xml format
        """
        date_parse = datetime.strptime(user_date, "%d.%m.%y")
        ansidate = date_parse.strftime("%Y-%m-%d") + "T" + datetime.now().strftime("%H:%M")
        ansienddate = date_parse.strftime("%Y-%m-%d")
        date = date_parse.strftime("%d/%b/%y")
        data = {
            "use-ISO8061-week-numbers": "false", "ansidate": ansidate, "ansienddate": ansienddate,
            "startTimeEnabled": "true", "tracker": "false", "planning": "false", "user": user_name,
            "issue": issue_id, "date": date, "enddate": date, "time": time_spent
            }
        result = self.__invoke_method_tempo("worklogs/{0}".format(issue_id), data)
        if not result:
            raise JiraException("Failed to worklog", 1)
        return result

    def check_permissions(self):
        result = self.__invoke_method_jira("mypermissions")
        if not result:
            raise JiraException("Authentication Failed", 2)
        if not result["permissions"]["WORKLOG_EDIT_ALL"]["havePermission"]:
            raise JiraException("You do not have permission to add worklog", 3)
        return True

    def get_issue_info(self, issue_id):
        result = self.__invoke_method_jira("issue/{0}".format(issue_id))
        if not result:
            raise JiraException("Get issue Failed", 4)
        return result

    def get_user_info(self, user_name):
        result = self.__invoke_method_jira("user?username={0}".format(user_name))
        if not result:
            raise JiraException("User {0} not found".format(user_name), 5)
        return result
