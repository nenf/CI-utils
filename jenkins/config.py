# -*- coding: utf-8 -*-

# USERNAME - Username authentication for jenkins API (required)
# JENKINS_TOKEN - API token - http://<jenkins>/user/<username>/configure (required)
# PROJECT_NAME - New project name, only lower case (required)
# JENKINS_SERVER - Jenkins url (required)
# JENKINS_VIEW_NAME - View name for jenkins (required)
# HIPCHAT_ROOM_ID - HipChat room id for send notification (optional)
# HIPCHAT_JENKINS_TOKEN - HipChat room token for send notification: https://<hipchat>/rooms/tokens/<room_id> (optional)
# GIT_REPOSITORY_URL - Repository url (required)
USERNAME = "*"
JENKINS_TOKEN = "*"

PROJECT_NAME = "*"
JENKINS_SERVER = "*"
JENKINS_VIEW_NAME = PROJECT_NAME

HIPCHAT_SERVER = "*"
HIPCHAT_ROOM_ID = "*"
HIPCHAT_JENKINS_TOKEN = "*"

GIT_REPOSITORY_URL = "*"
