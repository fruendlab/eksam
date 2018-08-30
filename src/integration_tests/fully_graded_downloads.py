import json

from eksam import testing


TIME_TO_RESPOND = 2


def isnan(x):
    return not x == x


with testing.server_running(TIME_TO_RESPOND):
    testing.submit_fake_answers()
    testing.get_grades()
    with open('grades.json') as f:
        grades = json.load(f)

    correct_answers = [False, True, True, False, True, False, False, True]

    assert len(grades) == 10
    for i, g in enumerate(grades):
        print(i, g)
        assert g['chapter'] == 1
        if g['student_id'] == '9999':
            for key in g:
                if key not in ['student_id', 'chapter']:
                    assert isnan(g[key])
            continue
        ncorrect = sum([(k < int(g['student_id'][0])) == a
                        for k, a in enumerate(correct_answers)])
        assert g['correct_answers'] == ncorrect
        assert g['total_answers'] == len(correct_answers)
        assert g['percentage'] == 100*ncorrect / len(correct_answers)
        assert g['scaled_percentage'] == g['percentage']/0.8
