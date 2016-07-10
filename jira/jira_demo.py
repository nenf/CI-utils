#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from jira_ci import JiraCI
from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser(description="Test script for work with jira api")
    parser.add_argument("-j", "--jira", help="Jira url", type=str, required=False, default="http://jira/")
    parser.add_argument("-u", "--user", help="Username authentication", type=str, required=False)
    parser.add_argument("-p", "--password", help="Password authentication", type=str, required=False)
    args = parser.parse_args()

    jira = JiraCI(args.jira, args.user, args.password)

    issue_id = "TEST-1"
    if not jira.check_issue_exist(issue_id):
        exit(-1)

    if jira.check_issue_state(issue_id, "open"):
        print "{0} is open".format(issue_id)
