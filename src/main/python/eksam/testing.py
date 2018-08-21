import subprocess
import os
import signal

from contextlib import contextmanager

@contextmanager
def server_running():
    subprocess.run('touch /tmp/test.db && rm /tmp/test.db', shell=True)
    with subprocess.Popen('eksam-server -s test /tmp/test.db -t {}'
                          .format(TIME_TO_RESPOND),
                          shell=True,
                          ) as server:
        time.sleep(2)  # Leave some time for the server to come up
        subprocess.run('eksam-cli -s test register example-students.yaml',
                       shell=True)
        subprocess.run('eksam-cli -s test statements example-statements.yaml',
                       shell=True)
        yield
        os.kill(server.pid, signal.SIGKILL)
