#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from os import path
from re import findall, sub
from jenkins_ci import JenkinsCI


class JobCreator:
    def __init__(self, jenkins_url, username, token, project_name, view_name, git_repository, hipchat_room_id,
                 hipchat_token):
        self.jenkins_ci = JenkinsCI(jenkins_url, username, token)
        self.project_name = project_name
        self.git_repository = git_repository
        self.view_name = view_name
        self.hipchat_room = hipchat_room_id
        self.hipchat_token = hipchat_token
        self.main_job = project_name
        self.build_job = project_name + "-build"
        self.publish_job = project_name + "_PublishArtifacts"
        self.jobs_list = [self.main_job, self.build_job, self.publish_job]
        self.necessary_plugins = ["jenkins-multijob-plugin", "git", "gitlab-plugin", "envinject",
                                  "parameterized-trigger", "ws-cleanup", "build-name-setter", "disk-usage",
                                  "copyartifact", "scp", "email-ext", "matrix-project", "xshell", "hipchat"]

    def __correct_plugins_version(self, xml_config):
        plugins_version_dict = self.jenkins_ci.get_plugins_version_dict(self.necessary_plugins)
        plugins_in_xml = set([sub("plugin=|\"", "", p) for p in findall("plugin=.*\"", xml_config)])

        for plugin_with_version in plugins_in_xml:
            plugin_name = plugin_with_version.split("@")[0]
            new_version = plugins_version_dict[plugin_name]
            xml_config = xml_config.replace(plugin_with_version, "{0}@{1}".format(plugin_name, new_version))
        return xml_config

    def __correct_variable(self, xml_config):
        xml_config = xml_config.replace("${JOB_CREATOR_GIT_URL}", self.git_repository)
        xml_config = xml_config.replace("${JOB_CREATOR_PROJECT_NAME}", self.main_job)
        xml_config = xml_config.replace("${JOB_CREATOR_BUILD_NAME}", self.build_job)
        xml_config = xml_config.replace("${JOB_CREATOR_ARTIFACTS_NAME}", self.publish_job)
        xml_config = xml_config.replace("${JOB_CREATOR_HIP_CHAT_TOKEN}", self.hipchat_token)
        xml_config = xml_config.replace("${JOB_CREATOR_HIP_CHAT_ROOM}", self.hipchat_room)
        return xml_config

    def __create_job_with_reconf(self, job_name, xml_config_name):
        execute_path = path.dirname(path.realpath(__file__))
        with open(path.join(execute_path, "template", xml_config_name), "r") as config:
            xml_config = config.read()

        xml_config = self.__correct_variable(xml_config)
        xml_config = self.__correct_plugins_version(xml_config)

        self.jenkins_ci.create_job(job_name, xml_config)

    def create_projects(self):
        if not self.jenkins_ci.plugins_checker(self.necessary_plugins):
            exit(1)

        if self.jenkins_ci.check_jobs_exist(self.jobs_list):
            exit(1)

        self.__create_job_with_reconf(self.main_job, "main_job.xml")
        self.__create_job_with_reconf(self.build_job, "build_job.xml")
        self.__create_job_with_reconf(self.publish_job, "publish_job.xml")

        self.jenkins_ci.create_view(self.view_name)
        for job in self.jobs_list:
            self.jenkins_ci.move_job_on_view(self.view_name, job)


if __name__ == "__main__":
    parser = ArgumentParser(description="Script for create multi project job. Script uses config.py")
    args = parser.parse_args()
    from config import *
    print "[*] : Jenkins - creating jobs"
    creator = JobCreator(JENKINS_SERVER, USERNAME, JENKINS_TOKEN, PROJECT_NAME, JENKINS_VIEW_NAME, GIT_REPOSITORY_URL,
                         HIPCHAT_JENKINS_TOKEN, HIPCHAT_JENKINS_TOKEN)
    creator.create_projects()
    job_url = "{0}/job/{1}".format(JENKINS_SERVER, PROJECT_NAME)
    print "Project '{0}' was created".format(PROJECT_NAME)
    print "Now, you can configure project: {0}".format(job_url)

