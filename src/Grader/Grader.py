import os
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

    def __init__(self, submission_dir, entry_point, input_dir, output_dir, timeout):
        self.submission_dir: str = submission_dir
        self.entry_point: str = entry_point
        self.input_dir: str = input_dir
        self.output_dir: str = output_dir
        self.timeout: int = timeout
        self.submissions: List[Submission] = []
        self.tests: List[Test] = []

    def init(self) -> 'Grader':
        self.init_submissions()
        self.init_tests()
        return self

    def init_submissions(self):
        for student in os.listdir(self.submission_dir):
            submission_path = os.path.join(self.submission_dir, student)
            if os.path.isdir(submission_path):
                self.submissions.append(Submission(submission_path, self.entry_point))

    def init_tests(self):
        for test in os.listdir(self.input_dir):
            input_path = os.path.join(self.input_dir, test)
            output_path = os.path.join(self.output_dir, test.replace(".in", ".out"))
            if os.path.isfile(input_path) and os.path.isfile(output_path):
                self.tests.append(Test(input_path, output_path))
        pass

    def run(self):
        for submission in self.submissions:
            if not submission.compiled():
                submission.ready()
                submission.compile()
            print(submission.student_id)
            if not self.generated(submission):
                self.generate(submission)
            if not self.graded(submission):
                self.grade(submission)

    def generate(self, submission):
        generated_path = os.path.join(submission.submission_path, "output")
        if not os.path.exists(generated_path):
            os.mkdir(generated_path)
        for test in self.tests:
            submission.run(test.input_path)

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

    def graded(self, submission):
        return True

    def grade(self, submission):
        pass

    def extract(self):
        return self.submissions
