from math import floor
from typing import List

from Grader.Grader import Grader
from Grader.Submission.Submission import Submission
import json
import os

SETTINGS: dict = json.load(open("resources/settings.json"))


def write_grades(grades: List[Submission]):
    with open("grades.csv", "w") as f:
        f.write("Student ID,Grade,Feedback\n")
        for grade in grades:
            student_id = grade.student_id.replace("p1_", "")
            student_id = student_id.replace("P1_", "")
            # new line characters inside the feedback will break the csv file, fix it
            feedback = format_feedback(grade.feedback)
            if feedback == "\"\"\"\"":
                feedback = "Incomplete or invalid submission. Please check your submission file and the submission " \
                           "instructions for more details. "
            f.write(f"{student_id},{floor(grade.points)},{feedback}\n")


def format_feedback(feedback: dict) -> str:
    formatted = []
    for key, value in feedback.items():
        # feedback[key] = value.replace(",", ";")
        formatted += [f"{key}: {value}"]
    # add leading and trailing double quotes
    formatted.sort()
    return "\"\"" + json.dumps(formatted)[1:-1].replace(",", ";") + "\"\""


def rename_submissions():
    for student_dir in os.listdir(SETTINGS["submission_dir"]):
        submission_path = os.path.join(SETTINGS["submission_dir"], student_dir)
        if os.path.isdir(submission_path):
            # Rename the student dir so that there are no white spaces
            os.rename(submission_path, submission_path.replace(" ", "_"))


# open the csv file check each student id
def valid_line(line):
    student_id = line.split(",")[0]
    if student_id.isdigit() and len(student_id) == 10:
        return True
    return False


def verify_grades():
    # Read the entire file into memory
    with open('grades.csv', 'r') as infile:
        lines = infile.readlines()

    # Create a new list of lines that meet your conditions
    new_lines = [line for line in lines if valid_line(line)]

    # Write the new list of lines back to the original file
    with open('grades.csv', 'w') as outfile:
        outfile.write("Student ID,Grade,Feedback\n")
        outfile.writelines(new_lines)


if __name__ == '__main__':
    # rename_submissions()
    grader = Grader(SETTINGS).initialize()
    grader.run()
    write_grades(grader.submissions)
    verify_grades()
