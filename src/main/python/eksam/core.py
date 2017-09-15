#!/usr/bin/env python

from random import shuffle

import jinja2
from flask import Flask, request, abort
from pony import orm
from itsdangerous import BadSignature

app = Flask(__name__)
db = orm.Database()
jinja_env = jinja2.Environment(
    loader=jinja2.PackageLoader('eksam', 'templates')
)


class Statement(db.Entity):
    text = orm.Required(str)
    correct_answer = orm.Required(bool)
    checked = orm.Required(bool)
    answers = orm.Set("Answer")


class Student(db.Entity):
    student_id = orm.PrimaryKey(str)
    answers = orm.Set("Answer")
    accomodation = orm.Required(float, default=1.)


class Answer(db.Entity):
    student = orm.Required(Student)
    statement = orm.Required(Statement)
    response = orm.Required(bool)
    correct = orm.Required(bool)


@orm.db_session()
def add_students(student_data):
    for student in student_data:
        print('Adding student', student)
        Student(student_id=str(student['id']),
                accomodation=float(student['accomodation']))


@orm.db_session()
def verify_student(student_id):
    try:
        student = Student[student_id]
    except orm.core.ObjectNotFound:
        return False
    return len(student.answers) == 0


@orm.db_session()
def get_accomodation(student_id):
    return Student[student_id].accomodation


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


# # # # # Routes


@app.route('/')
def main():
    return jinja_env.get_template('register.html.j2').render()


@app.route('/exam/', methods=['POST'])
def exam():
    student_id = request.form['student_id']
    statements = get_statements()
    shuffle(statements)
    if verify_student(student_id):
        accomodation = get_accomodation(student_id)
        return jinja_env.get_template('exam.html.j2').render(
            student_id=student_id,
            statements=statements,
            test_time_seconds=app.test_time_seconds*accomodation)
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

    return jinja_env.get_template('finish.html.j2').render(
        student_id=student_id,
        total_correct=total_correct,
        total_statements=total_statements)


@app.route('/api/statements/', methods=['POST'])
def api_statements():
    try:
        statements = app.signer.loads(request.data)
    except BadSignature:
        abort(401)
    add_statements(statements)
    return '', 200


@app.route('/api/students/', methods=['POST'])
def api_students():
    try:
        students = app.signer.loads(request.data)
    except BadSignature:
        abort(401)
    add_students(students)
    return '', 200
