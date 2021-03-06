#!/usr/bin/env python

from random import shuffle
from itertools import product
from functools import reduce

import jinja2
from flask import Flask, request, abort, jsonify
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
    answers = orm.Set('Answer')
    chapter = orm.Required('Chapter')


class Student(db.Entity):
    student_id = orm.PrimaryKey(str)
    answers = orm.Set('Answer')
    finished = orm.Set('Chapter')
    accomodation = orm.Required(float, default=1.)


class Answer(db.Entity):
    student = orm.Required(Student)
    statement = orm.Required(Statement)
    response = orm.Required(bool)
    correct = orm.Required(bool)


class Chapter(db.Entity):
    number = orm.PrimaryKey(int)
    statements = orm.Set(Statement)
    students_submitted = orm.Set(Student)


@orm.db_session()
def add_students(student_data):
    for student in student_data:
        if Student.exists(student_id=str(student['id'])):
            s = Student.get(student_id=str(student['id']))
            s.accomodation = float(student['accomodation'])
        else:
            print('Adding student', student)
            Student(student_id=str(student['id']),
                    accomodation=float(student['accomodation']))


@orm.db_session()
def verify_student(student_id, chapter_id):
    try:
        student = Student[student_id]
    except orm.core.ObjectNotFound:
        return False
    print('Checking chapter for student {}'.format(student_id))
    for c in student.finished:
        print('Student finished chapter {}'.format(c.number))
        if c.number == chapter_id:
            print('  Student has already finished this chapter!')
            return False
    else:
        return True


@orm.db_session()
def get_student_list():
    students = []
    all_students = (s for s in Student)
    for student in orm.select(all_students):
        students.append({'id': str(student.student_id),
                         'accomodation': student.accomodation,
                         'finished': [ch.number for ch in student.finished]})
    return students


@orm.db_session()
def get_accomodation(student_id):
    return Student[student_id].accomodation


@orm.db_session()
def get_statements(chapter, evaluate=False):
    result = orm.select(
        statement
        for statement in Statement
        if statement.chapter.number == int(chapter)
    ).order_by(Statement.id)
    out = []
    for statement in result:
        new_value = {'idx': statement.id,
                     'answer': statement.correct_answer,
                     'text': statement.text}
        if evaluate:
            answers = [int(a.correct) for a in statement.answers]
            if len(answers):
                new_value['correct'] = reduce(lambda x, y: x+y, answers)
                new_value['answers'] = len(answers)
            else:
                new_value['correct'] = 0
                new_value['answers'] = 0
        if statement.checked:
            new_value['status'] = 'checked'
        out.append(new_value)
    return out


@orm.db_session()
def write_answers(student_id, statements, answers, chapter):
    student = Student[student_id]
    for statement, answer in zip(statements, answers):
        Answer(student=student,
               statement=Statement[statement['idx']],
               response=answer,
               correct=answer == statement['answer'])
    student.finished.add(Chapter[int(chapter)])


@orm.db_session()
def update_statements(statements):
    for statement in statements:
        chapter = ensure_chapter(statement['chapter'])
        s = Statement.get(text=statement['text'])
        print('Found statement', s)
        if s:
            s.correct_answer = statement['answer']
            s.chapter = chapter
        else:
            Statement(text=statement['text'],
                      correct_answer=statement['answer'],
                      chapter=chapter,
                      checked='status' in statement)


@orm.db_session()
def duplicate_submission(student_id, chapter_id):
    student = Student[student_id]
    for chapter in student.finished:
        if chapter.number == int(chapter_id):
            return True
    else:
        return False


def ensure_chapter(chapter):
    if Chapter.exists(number=int(chapter)):
        return Chapter[int(chapter)]
    else:
        chapter = Chapter(number=int(chapter))
        db.commit()
        return chapter


def count_correct(answers, responses):
    count = 0
    for answer, response in zip(answers, responses):
        count += (answer == response)
    return count


@orm.db_session()
def get_grades(chapters):
    students = orm.select(s for s in Student)
    chapters = (Chapter[int(c)] for c in chapters)
    grades = []
    for student, chapter in product(students, chapters):
        if chapter not in student.finished:
            grades.append({'student_id': student.student_id,
                           'correct_answers': float('nan'),
                           'total_answers': float('nan'),
                           'percentage': float('nan'),
                           'chapter': chapter.number,
                           'scaled_percentage': float('nan')})
            continue
        ncorrect = 0
        ntotal = 0
        for statement in chapter.statements:
            answer = Answer.get(student=student,
                                statement=statement)
            ncorrect += answer.correct
            ntotal += 1
        grades.append({'student_id': student.student_id,
                       'correct_answers': ncorrect,
                       'total_answers': ntotal,
                       'percentage': 100*ncorrect/ntotal,
                       'chapter': chapter.number,
                       'scaled_percentage': 125*ncorrect/ntotal})
    return grades


# # # # # Routes


@app.route('/<int:chapter>/')
def main(chapter):
    with orm.db_session():
        if not Chapter.exists(number=int(chapter)):
            abort(404)

    return jinja_env.get_template('register.html.j2').render(chapter=chapter)


@app.route('/exam/<chapter>/', methods=['POST'])
def exam(chapter):
    student_id = request.form['student_id']
    statements = get_statements(chapter)
    shuffle(statements)
    if verify_student(student_id, chapter):
        accomodation = get_accomodation(student_id)
        return jinja_env.get_template('exam.html.j2').render(
            student_id=student_id,
            statements=statements,
            chapter=chapter,
            test_time_seconds=app.test_time_seconds*accomodation)
    else:
        abort(401)


@app.route('/finish/<chapter>/', methods=['POST'])
def finish(chapter):
    student_id = request.form['student_id']
    if duplicate_submission(student_id, chapter):
        abort(401)
    statements = get_statements(chapter)
    responses = ['statement{}'.format(s['idx']) in request.form
                 for s in statements]
    write_answers(student_id, statements, responses, chapter)
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
    update_statements(statements)
    return '', 200


@app.route('/api/statements/<chapter>/', methods=['GET'])
def api_get_statements(chapter):
    try:
        token = app.signer.loads(request.args.get('token'))
        if not token == 'token':
            raise BadSignature
    except BadSignature:
        abort(401)
    statement_list = get_statements(int(chapter), evaluate=True)
    return jsonify(statement_list), 200


@app.route('/api/students/', methods=['POST'])
def api_students():
    try:
        students = app.signer.loads(request.data)
    except BadSignature:
        abort(401)
    print('Students:', students)
    add_students(students)
    return '', 200


@app.route('/api/students/', methods=['GET'])
def api_get_students():
    try:
        token = app.signer.loads(request.args.get('token'))
        if not token == 'token':
            raise BadSignature
    except BadSignature:
        abort(401)
    student_list = get_student_list()
    return jsonify(student_list), 200


@app.route('/api/grades/', methods=['GET'])
def api_get_grades():
    try:
        chapters = app.signer.loads(request.args.get('chapters'))
    except BadSignature:
        abort(401)
    grades = get_grades(chapters)
    return jsonify(grades), 200
