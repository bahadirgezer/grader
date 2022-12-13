from Grader.Submission.Submission import Submission
import os
import json


def iterate_submissions(submissions_path: str):
    for student in os.listdir(submissions_path):
        submission_path = os.path.join(submissions_path, student)
        if os.path.isdir(submission_path):
            yield Submission(submission_path)


if __name__ == '__main__':
    # read the settings.json file and get the path to the submissions
    # settings = json.load(open("settings.json"))
    # iterate through the submissions and run the tests
    settings = json.load(open("../resources/settings.json"))
    # walk the subdirectories of submission_dir
    student_submissions = iterate_submissions(settings["submission_dir"])

