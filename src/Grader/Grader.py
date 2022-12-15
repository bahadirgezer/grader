import os
import json
from typing import List

from Grader.Submission.Submission import Submission
from Grader.Test.Test import Test


class Grader:
    def __init__(self, settings):
        self.submission_dir: str = settings["submission_dir"]
        self.entry_point: str = settings["entry_point"]
        self.input_dir: str = settings["input_dir"]
        self.output_dir: str = settings["output_dir"]
        self.timeout: int = settings["timeout"]
        self.submissions: List[Submission] = []
        self.tests: List[Test] = []

    def initialize(self) -> 'Grader':
        self.init_submissions()
        self.init_tests()
        return self

    def init_submissions(self):
        for student in os.listdir(self.submission_dir):
            submission_path = os.path.join(self.submission_dir, student)
            if os.path.isdir(submission_path):
                self.submissions.append(Submission(submission_path, self.entry_point))

    def init_tests(self):
        for test in sorted(os.listdir(self.input_dir)):
            if test.startswith("."):
                continue
            input_path = os.path.join(self.input_dir, test)
            output_path = os.path.join(self.output_dir, test.replace(".in", ".out"))
            if os.path.isfile(input_path) and os.path.isfile(output_path):
                self.tests.append(Test(input_path, output_path))

    def run(self):
        c = 0
        for submission in self.submissions:
            c += 1
            if c > 10:
                pass

            if not submission.compiled():
                submission.ready()
                submission.compile()

            if submission.student_id == "INVALID":
                continue
            print("{id} \033[3mprocessing...\033[0m".format(id=submission.student_id))

            if not submission.valid:
                self.grade(submission)
                continue

            if not self.generated(submission):
                self.generate(submission)

            self.grade(submission)

            print(json.dumps(submission.feedback))
            print(submission.points)

            if not self.intact_input_files():
                # copy the input files from the ../backup folder to the ../input folder
                for test in self.tests:
                    os.system("cp " + test.input_path.replace("inputs", "backup") + " " + test.input_path)

    def generate(self, submission):
        generated_path = os.path.join(submission.submission_path, "output")
        if not os.path.exists(generated_path):
            os.mkdir(generated_path)
        for test in self.tests:
            if not os.path.exists(os.path.join(generated_path, os.path.basename(test.input_path))):
                submission.run(test.input_path, self.timeout)

    def generated(self, submission):
        generated_path = os.path.join(submission.submission_path, "output")
        if not os.path.exists(generated_path):
            return False
        for test in self.tests:
            output_path = os.path.join(generated_path,
                                       os.path.basename(test.input_path).replace(".in", ".out"))
            if not os.path.exists(output_path):
                return False
        return True

    def grade(self, submission):
        points_per_test = 90 / len(self.tests)
        if not submission.valid:
            return
        if not submission.compiled():
            return
        submission.points += 10
        for test in self.tests:
            submission.points += points_per_test * test.grade(submission)

    def clear(self):
        for submission in self.submissions:
            submission.clear()

    # check if the input files are the same sizes as the copy of the input files in the ../backup folder
    def intact_input_files(self):
        for test in self.tests:
            # check if the input file is the same size as the copy of the input file in the ../backup folder
            if os.path.getsize(test.input_path) != os.path.getsize(test.input_path.replace("inputs", "backup")):
                print("input file size mismatch: " + test.input_path)
                return False
        return True
