import os

from typing import List

from Grader.Submission.Submission import Submission


# return true if the two lists have the same contents, false otherwise
# the items can be in random order
def identical_content_unordered(list1: List[str], list2: List[str]) -> bool:
    if len(list1) != len(list2):
        return False
    for item in list1:
        if item not in list2:
            return False
    return True


# <acc> <termination> <atc1> <atc2> <atc3> ... <atcN>
def parse_output(output: str) -> dict:
    lines: List[str] = output.splitlines()
    parsed: dict = dict()
    for line in lines:
        tokens: List[str] = line.split()
        if len(tokens) < 2:
            continue
        acc: str = tokens[0]
        try:
            termination: int = int(tokens[1])
        except ValueError:
            continue
        atc_list: List[str] = tokens[2:]
        parsed[acc] = (termination, atc_list)
    return parsed


# return a string repr of a list where if the list is too long the middle is replaced with ...
# modify the resulting string so that the three dots are not surrounded by quotes
def list_repr(l: List[str]) -> str:
    if len(l) > 6:
        return str(l[:4] + ["..."] + l[-2:]).replace(" , ", ",").replace("'", "")
    else:
        return str(l)

class Test:
    def __init__(self, input_path, output_path):
        self.input_path: str = input_path
        self.output_path: str = output_path

    # grade the submission output against the test output
    # check if the file in the output path is the same as the file in submission output path
    def grade(self, submission: Submission) -> float:
        case_name = os.path.basename(self.input_path).replace(".in", "")
        if case_name in submission.feedback:
            return 0.0
        submission_output_path = os.path.join(submission.submission_path,
                                              "output", os.path.basename(self.output_path))
        if not os.path.exists(submission_output_path):
            submission.feedback[case_name] = "No output file found."
            return 0.0
        expected: str = open(self.output_path, "r").read()
        try:
            actual: str = open(submission_output_path, "r").read()
        except UnicodeDecodeError:
            submission.feedback[case_name] = "Output file decoding error."
            return 0.0

        expected_parsed: dict = parse_output(expected)
        actual_parsed: dict = parse_output(actual)
        expeced_accs: List[str] = list(expected_parsed.keys())

        percentage: float = 0.0
        per_line: float = 1.0 / len(expeced_accs)
        termination_point_per_line: float = 0.6
        atc_point_per_line: float = 0.4

        missing_accs: List[str] = []
        wrong_terminations: List[str] = []
        wrong_atcs: List[str] = []
        for acc in expeced_accs:
            if acc not in actual_parsed:
                # feedback += f"ACC line {acc} not found.\n"
                missing_accs.append(acc)
                continue
            expected_termination, expected_atc_list = expected_parsed[acc]
            actual_termination, actual_atc_list = actual_parsed[acc]
            if expected_termination != actual_termination:
                # feedback += f"ACC line {acc} expected {expected_termination} got {actual_termination} " \
                #         "for termination time.\n"
                wrong_terminations.append(acc)
            else:
                percentage += per_line * termination_point_per_line

            if not identical_content_unordered(expected_atc_list, actual_atc_list):
                # feedback += f"ACC line {acc} expected {expected_atc_list} got {actual_atc_list} " \
                #         "for the ATC codes list.\n"
                wrong_atcs.append(acc)
            else:
                percentage += per_line * atc_point_per_line

        passed: bool = len(missing_accs) == 0 and len(wrong_terminations) == 0 and len(wrong_atcs) == 0
        feedback: str = f""
        if len(missing_accs) > 0:
            feedback += f"Missing ACC line(s) {list_repr(missing_accs)} "
        if len(wrong_terminations) > 0:
            feedback += f"Wrong termination times for ACC line(s) {list_repr(wrong_terminations)} "
        if len(wrong_atcs) > 0:
            feedback += f"Wrong ATC codes for ACC line(s) {list_repr(wrong_atcs)} "
        if passed:
            feedback += "Passed "
        feedback = feedback[:-1] + "."

        submission.feedback[case_name] = feedback
        return percentage
