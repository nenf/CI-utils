# -*- coding: utf-8 -*-

# GITLAB_TOKEN - API token - http://<gitlab>/profile/personal_access_tokens (required)
# PROJECT_NAME - New project name, only lower case (required)
# PROJECT_DESCRIPTION - Project description (optional)
# GITLAB_SERVER - Gitlab url (required)
# GITLAB_NAMESPACE - Namespace gitlab (required)
# GITLAB_CI_BOT_NAME - Username for gitlab jenkins service (optional)
# GITLAB_CI_BOT_PASSWORD - Password for gitlab jenkins service (optional)
# JENKINS_SERVER - Jenkins url (required)
# HIPCHAT_SERVER - HipChat url (required)
# HIPCHAT_ROOM_ID - HipChat room id for send notification (optional)
# HIPCHAT_SCM_TOKEN - HipChat room token for send notification: https://<hipchat>/rooms/tokens/<room_id> (optional)
GITLAB_TOKEN = "*"

PROJECT_NAME = "*"
PROJECT_DESCRIPTION = "*"

GITLAB_SERVER = "*"
GITLAB_NAMESPACE = "*"
GITLAB_SCM_BOT_NAME = "*"
GITLAB_SCM_BOT_PASSWORD = "*"

JENKINS_SERVER = "*"

HIPCHAT_SERVER = "*"
HIPCHAT_ROOM_ID = "*"
HIPCHAT_SCM_TOKEN = "*"
