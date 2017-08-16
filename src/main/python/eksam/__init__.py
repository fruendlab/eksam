#!/usr/bin/env python

from flask import Flask, render_template, request, abort
from pony import orm
import jwt

TEST_TIME_SECONDS = 10

app = Flask(__name__)
db = orm.Database()


class Statement(db.Entity):
    text = orm.Required(str)
    correct_answer = orm.Required(bool)
    checked = orm.Required(bool)
    answers = orm.Set("Answer")


class Student(db.Entity):
    student_id = orm.PrimaryKey(str)
    answers = orm.Set("Answer")


class Answer(db.Entity):
    student = orm.Required(Student)
    statement = orm.Required(Statement)
    response = orm.Required(bool)
    correct = orm.Required(bool)


# db.bind(provider='sqlite', filename='student_data.db', create_db=True)
db.bind(provider='sqlite', filename=':memory:')
print("Generating Mapping")
db.generate_mapping(create_tables=True)


@orm.db_session()
def add_students(student_ids):
    for student_id in student_ids:
        Student(student_id=str(student_id))


def verify_token(token):
    decoded = jwt.decode(token, 'sensation_and_perception')
    return decoded['name'] == 'admin'


@orm.db_session()
def verify_student(student_id):
    try:
        student = Student[student_id]
    except orm.core.ObjectNotFound:
        return False
    return len(student.answers) == 0


@orm.db_session()
def get_statements():
    result = orm.select(
        statement for statement in Statement
    ).order_by(Statement.id)
    out = []
    for statement in result:
        new_value = {'idx': statement.id,
                     'answer': statement.correct_answer,
                     'text': statement.text}
        if statement.checked:
            new_value['status'] = 'checked'
        out.append(new_value)
    return out


@orm.db_session()
def write_answers(student_id, statements, answers):
    student = Student[student_id]
    for statement, answer in zip(statements, answers):
        Answer(student=student,
               statement=Statement[statement['idx']],
               response=answer,
               correct=answer == statement['answer'])


@orm.db_session()
def add_statements(statements):
    for statement in statements:
        Statement(text=statement['text'],
                  correct_answer=statement['answer'],
                  checked='status' in statement)


def count_correct(answers, responses):
    count = 0
    for answer, response in zip(answers, responses):
        count += (answer == response)
    return count


@app.route('/')
def main():
    return render_template('register.html.j2')


@app.route('/exam/', methods=['POST'])
def exam():
    student_id = request.form['student_id']
    statements = get_statements()
    if verify_student(student_id):
        return render_template('exam.html.j2',
                               student_id=student_id,
                               statements=statements,
                               test_time_seconds=TEST_TIME_SECONDS)
    else:
        abort(401)


@app.route('/finish/', methods=['POST'])
def finish():
    student_id = request.form['student_id']
    statements = get_statements()
    print(request.form)
    responses = ['statement{}'.format(s['idx']) in request.form
                 for s in statements]
    write_answers(student_id, statements, responses)
    total_correct = count_correct((s['answer'] for s in statements), responses)
    total_statements = len(statements)

    return render_template('finish.html.j2',
                           student_id=student_id,
                           total_correct=total_correct,
                           total_statements=total_statements)


@app.route('/api/statements/', methods=['POST'])
def api_statements():
    if verify_token(request.json['token']):
        add_statements(request.json['statements'])
        return '', 200
    else:
        abort(401)


@app.route('/api/students/', methods=['POST'])
def api_students():
    if verify_token(request.json['token']):
        add_students(request.json['students'])
        return '', 200
    else:
        abort(401)
