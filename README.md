CI scripts for starting new projects and working with Jenkins, GitLab, Jira, Tempo Plugin

1. Install requirements modules:

```bash
$ pip install -r requirements.txt
```

2. Edit config.py

```bash
./config.py
./gitlab/config.py
./hipchat/config.py
./jenkins/config.py
```

### Create a new GitLab repository:

```bash
$ ./gitlab/repo_creator.py
```

### Create new Jobs in Jenkins:

```bash
$ ./jenkins/job_creator.py
```

### Create new room in HipChat:

```bash
$ ./hipchat/hipchat_creator.py
```

### Logging work on an issues in jira:
```bash
$ cd tempo
$ ./record_tempo.py -d 11.03.16
```
