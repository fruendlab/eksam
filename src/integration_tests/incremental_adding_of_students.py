import time
import yaml

from eksam import testing


TIME_TO_RESPOND = 2

with testing.server_running(TIME_TO_RESPOND):
    testing.register_students('example-students-2.yaml')
    print('Finished student registration')
    time.sleep(2)
    students = testing.list_students()

    with open('example-students-2.yaml') as f:
        expected = yaml.load(f)
    for student in expected:
        student_id = student['id']
        candidates = [s for s in students if s['id'] == student_id]
        assert len(candidates) == 1
        assert candidates[0]['accomodation'] == student['accomodation']

    print('OK')
