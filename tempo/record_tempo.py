#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from pyexcel import get_sheet, get_records
from tempo import TempoRecord, JiraException
from argparse import ArgumentParser
from os import path
from re import search


def check_file_exist(path_to_file):
    if not path.exists(path_to_file):
        print "File {0} doesn't exist".format(path_to_file)
        exit(1)


def check_total_time(records, users_list, total_hours):
    valid = True
    for user in users_list:
        sum_hours = sum([int(record[user]) for record in records if record[user] != ""])
        if total_hours != sum_hours:
            print "Error: {0}({1}) hours for {2}".format(sum_hours, total_hours, user)
            valid = False
    return valid


def get_jira_project_dict(file_with_projects):
    with open(file_with_projects) as hf:
        return dict(x.rstrip().split(None, 1) for x in hf)


if __name__ == "__main__":
    parser = ArgumentParser(description="Script for logging work on an issue")
    parser.add_argument("-t", "--total", help="Total hours, default: 35", type=int, required=False, default=35)
    parser.add_argument("-c", "--csv", help="Path to csv file, default: ./timesheet.csv", type=str, required=False,
                        default="timesheet.csv")
    parser.add_argument("-p", "--projects", help="Path to file with projects, default: ./projects", type=str,
                        required=False, default="projects")
    parser.add_argument("-d", "--date", help="Date in d.m.y format, like 11.03.16", type=str, required=True)
    parser.add_argument("-u", "--username", help="Username authentication for Jira", type=str, required=False)
    parser.add_argument("-s", "--secret", help="Password authentication for Jira", type=str, required=False)
    parser.add_argument("-j", "--jira", help="Jira url", type=str, required=False, default="http://jira")
    args = parser.parse_args()

    check_file_exist(args.csv)
    check_file_exist(args.projects)

    try:
        tempo = TempoRecord(args.jira, args.username, args.secret)
    except JiraException as e:
        print e.message
        exit(e.code)

    try:
        sheet = get_sheet(file_name=args.csv)
        records = get_records(file_name=args.csv)
        issues_dict = get_jira_project_dict(args.projects)

        users = sheet.row[0][1:]
        projects = sheet.column[0][1:]
    except Exception as e:
        print e
        exit(1)

    # Check the total number of hours
    if not check_total_time(records, users, args.total):
        exit(1)

    # Check user info
    for user in users:
        try:
            tempo.get_user_info(user)
        except JiraException as e:
            print e.value
            exit(e.code)

    # Check projects info
    for project in projects:
        try:
            tempo.get_issue_info(issues_dict[project])
        except JiraException as e:
            print e.value
            exit(e.code)
        except Exception as e:
            print e
            exit(1)

    # Logging work on an issue
    for record in records:
        project_name = record["project"]
        issue_id = issues_dict[project_name]
        print "Logging {0} ({1})".format(project_name, issue_id)
        for user in users:
            if record[user]:
                xml_response = tempo.worklog(issue_id, user, args.date, record[user])
                if search("valid=\"true\"", xml_response):
                    print "\t[+] User: {0}, {1} hours".format(user, record[user])
                else:
                    print "\t[-] Worklog failed for user: {0}, {1} hours".format(user, record[user])
                    print xml_response
