import subprocess
import yaml
import os
import signal
import time
import requests

from contextlib import contextmanager


@contextmanager
def server_running(time_to_respond):
    subprocess.run('touch /tmp/test.db && rm /tmp/test.db', shell=True)
    server = subprocess.Popen('eksam-server -s test /tmp/test.db -t {}'
                              .format(time_to_respond),
                              shell=True)
    time.sleep(2)  # Leave some time for the server to come up
    register_students()
    upload_statements()
    yield
    server.terminate()
    os.kill(server.pid, signal.SIGKILL)


def register_students(fname='example-students.yaml'):
    subprocess.run('eksam-cli -s test register {}'.format(fname), shell=True)


def upload_statements(fname='example-statements.yaml'):
    subprocess.run('eksam-cli -s test statements {}'.format(fname), shell=True)


def list_students():
    students = subprocess.check_output('eksam-cli -s test list-students',
                                       shell=True)
    lines = []
    yaml_started = False
    students = students.decode('utf-8').splitlines()
    for line in students:
        if len(line) == 0:
            continue
        if line[0] == '-':
            yaml_started = True
        if yaml_started:
            lines.append(line)
    students = '\n'.join(lines)

    s = yaml.load(str(students))
    return s


def list_statements(chapter):
    statements = subprocess.check_output(
        'eksam-cli -s test list-statements {}'.format(chapter),
        shell=True)
    statements = statements.decode('utf-8').splitlines()
    yaml_started = False
    lines = []
    for line in statements:
        if len(line) == 0:
            continue
        if line[0] == '-':
            yaml_started = True
        if yaml_started:
            lines.append(line)
    statements = '\n'.join(lines)
    s = yaml.load(str(statements))
    return s


def submit_fake_answers():
    chapter = 1
    students = [str(i)*4 for i in range(10)]
    statements = list_statements(chapter)
    url = 'http://127.0.0.1:5000'

    for n, student in enumerate(students):
        payload = {'student_id': student}
        for i in range(n):
            if i < len(statements):
                payload['statement{}'.format(statements[i]['idx'])] = True
        if n == 9:
            break
        r = requests.post(url + '/finish/{}/'.format(chapter),
                          data=payload)
        print(r.status_code)


def get_grades():
    chapter = 1
    grades = subprocess.check_output(
        'eksam-cli -s test fetch {}'.format(chapter),
        shell=True)
    print(grades)
