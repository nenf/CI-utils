#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from json import loads, dumps
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError
from urlparse import urljoin


class GitlabException(Exception):
    def __init__(self, value, code):
        self.value = value
        self.code = code

    def __str__(self):
        return repr(self.value)


class Gitlab:
    def __init__(self, gitlab_url, username=None, password=None, token=None):
        self.gitlab_url = gitlab_url
        self.api_url = gitlab_url + "/api/v3/"
        self.headers = {"Accept": "application/json", "Content-type": "application/json"}
        if not token:
            self.token = self.__authentication(username, password)
        else:
            self.token = token

    def __authentication(self, username, password):
        if not username or password:
            raise GitlabException("Username or password cannot be empty", 1)

        token = self.__get_token(username, password)
        if not token:
            raise GitlabException("Cannot get token for {0}".format(username), 2)
        return token

    def __invoke_method(self, command, method="GET", parameters=None):
        if parameters is None:
            parameters = {}

        method_url = urljoin(self.api_url, command)
        request_data = None

        if method == "GET":
            query_string = urlencode(parameters)
            method_url = method_url + "?" + query_string
        else:
            request_data = dumps(parameters)

        self.headers["PRIVATE-TOKEN"] = self.token
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

    def __get_token(self, username, password):
        method_url = self.api_url + "session"
        request_data = urlencode({"login": username, "password": password})
        req = Request(method_url, data=request_data)
        try:
            response = urlopen(req).read()
        except HTTPError as e:
            print e
            return None
        user_object = loads(response.decode("utf-8"))
        return user_object["private_token"]

    def get_projects(self):
        result = self.__invoke_method("projects")
        if not result:
            raise GitlabException("Cannot get projects info", 1)
        return result

    def activate_hipchat(self, project_id, hipchat_server, room_id, room_token, color="purple"):
        parameters = {"token": room_token, "room": room_id, "server": hipchat_server, "color": color,
                      "notify": "1", "build_events": "1"}
        result = self.__invoke_method("projects/{0}/services/hipchat".format(project_id), "PUT", parameters)
        if not result:
            raise GitlabException("Cannot activate hipchat service", 2)
        return result

    def deactivate_hipchat(self, project_id):
        result = self.__invoke_method("projects/{0}/services/hipchat".format(project_id), "DELETE")
        if not result:
            raise GitlabException("Cannot deactivate hipchat service", 3)
        return result

    def activate_jenkins(self, project_id, jenkins_server, project_name, username, password):
        parameters = {"jenkins_url": jenkins_server, "project_name": project_name, "username": username,
                      "password": password, "push_events": 0, "tag_push_events": 1}
        result = self.__invoke_method("projects/{0}/services/jenkins".format(project_id), "PUT", parameters)
        if not result:
            raise GitlabException("Cannot activate jenkins service", 4)
        return result

    def deactivate_jenkins(self, project_id):
        result = self.__invoke_method("projects/{0}/services/jenkins".format(project_id), "DELETE")
        if not result:
            raise GitlabException("Cannot deactivate jenkins service", 5)
        return result

    def get_namespace(self):
        result = self.__invoke_method("namespaces", "GET")
        if not result:
            raise GitlabException("Cannot get namespace", 6)
        return result

    def get_namespace_id_by_name(self, namespace):
        for namespace_obj in self.get_namespace():
            if namespace_obj["path"].upper() == namespace.upper():
                return namespace_obj["id"]
        return None

    def create_projcet(self, name_project, namespace, description=""):
        if type(namespace) != int:
            namespace = self.get_namespace_id_by_name(namespace)
        parameters = {"name": name_project, "description": description, "namespace_id": namespace}
        result = self.__invoke_method("projects", "POST", parameters)
        if not result:
            raise GitlabException("Cannot create {0} project in {1} space".format(name_project, namespace), 7)
        return result

    def get_project(self, project_name):
        for projects_obj in self.get_projects():
            if projects_obj["path"] == project_name:
                return projects_obj
        raise GitlabException("Project {0} not found".format(project_name), 8)

    def get_projcet_id_by_name(self, project_name):
        return self.get_project(project_name)["id"]

    def remove_projcet(self, name_project):
        id_project = self.get_projcet_id_by_name(name_project)
        parameters = {"id": id_project}
        result = self.__invoke_method("projects", "DELETE", parameters)
        if not result:
            raise GitlabException("Cannot remove {0} project", 9)
        return result

    def get_http_url_to_repo(self, project_name):
        return self.get_project(project_name)["http_url_to_repo"]
