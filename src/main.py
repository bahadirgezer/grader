from Grader.Grader import Grader
from Grader.Submission.Submission import Submission
import os
import json

SETTINGS: dict = json.load(open("resources/settings.json"))


def iterate_submissions(submissions_path: str):
    for student in os.listdir(submissions_path):
        submission_path = os.path.join(submissions_path, student)
        if os.path.isdir(submission_path):
            yield Submission(submission_path, SETTINGS["entry_point"])


if __name__ == '__main__':

    grader: Grader = Grader(SETTINGS["submissions_path"], SETTINGS["entry_point"])
    grader.init_submissions()
    grader.run()
    grader.grade()

    '''
    student_submissions = iterate_submissions(SETTINGS["submission_dir"])
    for submission in student_submissions:
        submission.ready()
        submission.compile()

        if not submission.compiled():
            submission.ready()
            submission.compile()
        print(submission.student_id)
        submission.run()
    '''
