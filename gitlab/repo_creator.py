#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from gitlab import Gitlab


class RepoCreator:
    def __init__(self, gitlab_url, gitlab_token, project_name, namespace, description, jenkins_server,
                 jenkins_username, jenkins_password, hipchat_server, room_id, room_token):
        self.gitlab = Gitlab(gitlab_url, token=gitlab_token)
        self.project_name = project_name
        self.namespace = namespace
        self.description = description

        self.jenkins_server = jenkins_server
        self.jenkins_project_name = project_name
        self.jenkins_username = jenkins_username
        self.jenkins_password = jenkins_password
        self.hipchat_server = hipchat_server
        self.room_id = room_id
        self.room_token = room_token

    def make_new_project(self):
        self.gitlab.create_projcet(self.project_name, self.description, self.namespace)
        self.activate_services()

    def activate_services(self):
        project_id = self.gitlab.get_projcet_id_by_name(self.project_name)
        self.gitlab.activate_hipchat(project_id, self.hipchat_server, self.room_id, self.room_token)
        self.gitlab.activate_jenkins(project_id, self.jenkins_server, self.project_name, self.jenkins_username,
                                     self.jenkins_password)


if __name__ == "__main__":
    parser = ArgumentParser(description="Script for create repository on gitlab. Script uses config.py")
    args = parser.parse_args()
    from config import *
    print "[*] : Gitlab - creating project"
    g_creator = RepoCreator(GITLAB_SERVER, GITLAB_TOKEN, PROJECT_NAME, GITLAB_NAMESPACE, PROJECT_DESCRIPTION,
                            JENKINS_SERVER, GITLAB_SCM_BOT_NAME, GITLAB_SCM_BOT_PASSWORD, HIPCHAT_SERVER,
                            HIPCHAT_ROOM_ID, HIPCHAT_SCM_TOKEN)
    g_creator.make_new_project()
    print "Repository '{0}' was created".format(PROJECT_NAME)
    print "Now, you can configure project: {0}".format(g_creator.gitlab.get_http_url_to_repo(PROJECT_NAME))

