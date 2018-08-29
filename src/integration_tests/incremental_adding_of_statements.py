import time
import yaml

from eksam import testing


TIME_TO_RESPOND = 2

with testing.server_running(TIME_TO_RESPOND):
    testing.upload_statements('example-statements-2.yaml')
    time.sleep(2)
    statements = testing.list_statements(2)
    print('statements =', statements)

    assert len(statements) == 4
    s = [s for s in statements if s['text'] == 'Talk is cheap'][0]
    assert s['answer'] is False

    s = [s for s in statements
         if s['text'] == 'A triangle has three corners.']
    assert len(s) == 0

    statements = testing.list_statements(3)
    assert len(statements) == 2
    expected = set(['A triangle has three corners.',
                    'New question'])
    assert set([s['text'] for s in statements]) == expected

    print('OK')
