from eksam.testing import server_running
import requests

TIME_TO_RESPOND = 2


def test_chapter_not_existing():
    r = requests.get('http://127.0.0.1:5000/10/')
    assert r.status_code == 404
    print('OK')


with server_running(TIME_TO_RESPOND):
    test_chapter_not_existing()
