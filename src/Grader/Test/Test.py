import os

from Grader.Submission.Submission import Submission


class Test:
    def __init__(self, input_path, output_path):
        self.input_path: str = input_path
        self.output_path: str = output_path

    # grade the submission output against the test output
    # check if the file in the output path is the same as the file in submission output path
    def grade(self, submission: Submission):
        case_name = os.path.basename(self.input_path).replace(".in", "")
        if case_name in submission.feedback:
            return False
        submission_output_path = os.path.join(submission.submission_path,
                                              "output", os.path.basename(self.output_path))
        if not os.path.exists(submission_output_path):
            submission.feedback[case_name] = "No output file found."
            return False
        expected: str = open(self.output_path, "r").read()
        try:
            actual: str = open(submission_output_path, "r").read()
        except UnicodeDecodeError:
            submission.feedback[case_name] = "Output file decoding error."
            return False

        # check line by line, ignore empty lines and white spaces
        expected_lines = [line.strip() for line in expected.splitlines() if line.strip()]
        actual_lines = [line.strip() for line in actual.splitlines() if line.strip()]
        if len(expected_lines) != len(actual_lines):
            submission.feedback[case_name] = "Output file has {actual} lines, expected {expected} lines.".format(
                actual=len(actual_lines), expected=len(expected_lines))
            return False
        for expected_line, actual_line in zip(expected_lines, actual_lines):
            if expected_line != actual_line:
                submission.feedback[case_name] = "Expected: {expected}, Actual: {actual}".format(
                    expected=expected_line, actual=actual_line)
                return False
        submission.feedback[case_name] = "Passed."
        return True
