import subprocess
import yaml
import os
import signal
import time

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
