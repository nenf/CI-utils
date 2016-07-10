#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from time import sleep
from jenkinsapi.jenkins import Jenkins
from json import loads, dumps
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError
from urlparse import urljoin


class JenkinsException(Exception):
    def __init__(self, value, code):
        self.value = value
        self.code = code

    def __str__(self):
        return repr(self.value)


class JenkinsCI:
    def __init__(self, jenkins_url, username, password):
        self.jenkins_url = jenkins_url
        self.jenkins = Jenkins(self.jenkins_url, username=username, password=password)
        self.build_info = []
        __user_data = "Basic " + (username + ":" + password).encode("base64").rstrip()
        self.__headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": __user_data}

    def __invoke_method(self, command, method="GET", parameters=None, silent=False):
        if parameters is None:
            parameters = {}

        method_url = urljoin(self.jenkins_url, command)
        request_data = None

        if method == "GET":
            query_string = urlencode(parameters)
            method_url = method_url + "?" + query_string
        else:
            request_data = urlencode(parameters)

        req = Request(method_url, data=request_data, headers=self.__headers)
        req.get_method = lambda: method
        try:
            response = urlopen(req).read()
        except HTTPError as e:
            if not silent:
                print "{0} : {1}".format(method_url, e)
            return None

        try:
            return loads(response.decode("utf-8"))
        except ValueError:
            return response.decode("utf-8")

    def create_job(self, job_name, xml_config):
        try:
            self.jenkins.create_job(job_name, xml_config)
        except Exception as e:
            print e
            return False
        else:
            print "[+] : job {0} created".format(job_name)
            return True

    def format_path_folder(self, path_folder):
        return "job/" + path_folder.replace("/", "/job/")

    def rename_folder(self, path_folder, new_path_folder):
        new_folder_name = new_path_folder.split("/")[-1]
        command = "{0}/doRename".format(self.format_path_folder(path_folder))
        json_parameters = dumps({"newName": new_folder_name})
        parameters = {"newName": new_folder_name, "Submit": "Yes", "json": json_parameters}
        result = self.__invoke_method(command, "POST", parameters)
        if not result:
            raise JenkinsException("Cannot rename folder {0} to {1}".format(path_folder, new_path_folder), 1)
        print "[+] : folder {0} renamed to {1}".format(path_folder, new_path_folder)

    def create_folder(self, path_folder, recursive=False):
        if recursive:
            return self.recursive_create_folders(path_folder)
        split_path = path_folder.split("/")
        folder_name = split_path[-1]
        command = "createItem"
        if len(split_path) > 1:
            new_path = "/".join(f for f in split_path[:-1])
            command = self.format_path_folder(new_path) + "/" + command

        json_parameters = dumps({"name": folder_name, "mode": "com.cloudbees.hudson.plugins.folder.Folder",
                                 "from": "", "Submit": "OK"})
        parameters = {"name": folder_name, "mode": "com.cloudbees.hudson.plugins.folder.Folder",
                      "from": "", "Submit": "OK", "json": json_parameters}
        result = self.__invoke_method(command, "GET", parameters)
        if not result:
            raise JenkinsException("Cannot create folder {0}".format(path_folder), 1)
        print "[+] : folder {0} created".format(path_folder)

    def recursive_create_folders(self, path_folder):
        split_path = path_folder.split("/")
        root = split_path[0]
        for folder in split_path[1:]:
            if not self.check_folder_exist(root):
                self.create_folder(root)
            root += "/{0}".format(folder)

    def check_folder_exist(self, path_folder):
        result = self.__invoke_method(self.format_path_folder(path_folder), "GET", silent=True)
        if result:
            return True
        return False

    def move_job_on_folder(self, job_name, path_folder):
        command = "{0}/move/move".format(self.format_path_folder(job_name))
        json_parameters = {"destination": "/{0}".format(path_folder)}
        parameters = {"destination": "/{0}".format(path_folder), "json": json_parameters, "Submit": "Move"}
        result = self.__invoke_method(command, "POST", parameters)
        if not result:
            raise JenkinsException("Cannot move job {0} to {1} folder".format(job_name, path_folder), 2)
        print "[+] : Job {0} moved to {1} folder".format(job_name, path_folder)

    def get_plugins_version_dict(self, plugins_name_list):
        plugins_version_dict = {}
        all_plugins = self.jenkins.get_plugins().get_plugins_dict()
        for plugin in plugins_name_list:
            plugins_version_dict[plugin] = all_plugins[plugin].version
        return plugins_version_dict

    def copy_job(self, template_job, new_job):
        try:
            self.jenkins.copy_job(template_job, new_job)
        except Exception as e:
            print e
            return False
        else:
            print "[+] : Job {0} created".format(new_job)
            return True

    def plugins_checker(self, plugins_list):
        all_installed = True
        for plugin in plugins_list:
            if not self.jenkins.has_plugin(plugin):
                all_installed = False
                print "[-] : Plugin {0} is not installed".format(plugin)
        if not all_installed:
            return False
        return True

    def check_job_exist(self, job_name):
        if self.jenkins.has_job(job_name):
            return True
        return False

    def check_jobs_exist(self, jobs_list):
        status_exist = False
        for job in jobs_list:
            if self.check_job_exist(job):
                print "[-] : Job {0} already exist".format(job)
                status_exist = True
        return status_exist

    def create_view(self, view_name):
        views = self.jenkins.views
        if view_name not in views.keys():
            views.create(view_name)
            print "[+] : view {0} created".format(view_name)

    def move_job_on_view(self, view_name, job_name):
        view_url = "{0}/view/{1}".format(self.jenkins_url, view_name)
        view = self.jenkins.get_view_by_url(view_url)
        view.add_job(job_name)

    def delete_job(self, job_name):
        if self.check_job_exist(job_name):
            self.jenkins.delete_job(job_name)
            print "[+] : job {0} deleted".format(job_name)

    def build_job(self, job_name, arguments):
        job = self.jenkins.get_job(job_name)
        build_number = job.get_next_build_number()
        job.invoke(build_params=arguments)
        return build_number

    def get_git_info_build(self, job_name, build_number):
        job = self.jenkins.get_job(job_name)
        build = job.get_build(build_number)
        return build.get_revision()

    def get_url_build(self, job_name, build_number):
        return "{0}/job/{1}/{2}".format(self.jenkins_url, job_name, build_number)

    def print_info_build(self, job_name, build_number):
        url = self.get_url_build(job_name, build_number)
        git_info = self.get_git_info_build(job_name, build_number)

        print "Job: {0} #{1}".format(job_name, build_number)
        print "Url: {0}".format(url)
        for info in git_info:
            print "Branch : {0} | Revision : {1}".format(info["name"], info["SHA1"])
