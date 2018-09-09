#!/bin/bash

pip uninstall -y eksam
pyb install

killall -9 eksam-server
python src/integration_tests/normal_pass_through.py
NORMAL_PASS_TROUGH=$?

killall -9 eksam-server
python src/integration_tests/incremental_adding_of_students.py
ADDING_STUDENTS=$?

killall -9 eksam-server
python src/integration_tests/incremental_adding_of_statements.py
ADDING_STATEMENTS=$?

killall -9 eksam-server
python src/integration_tests/fully_graded_downloads.py
GRADED_DOWNLOADS=$?

killall -9 eksam-server
python src/integration_tests/chapter_does_not_exist.py
CHAPTER_NOT_EXIST=$?

killall -9 eksam-server

echo Normal pass through: $NORMAL_PASS_TROUGH
echo Adding students: $ADDING_STUDENTS
echo Adding statements: $ADDING_STATEMENTS
echo Graded downloads: $GRADED_DOWNLOADS
echo Chapter does not exist: $CHAPTER_NOT_EXIST
