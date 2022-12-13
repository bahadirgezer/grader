from typing import List

from Grader.Grader import Grader
from Grader.Submission.Submission import Submission
import json

SETTINGS: dict = json.load(open("resources/settings.json"))


def write_grades(grades: List[Submission]):
    with open("grades.csv", "w") as f:
        f.write("Student ID,Grade,Feedback\n")
        for grade in grades:
            student_id = grade.student_id.replace("p1_", "")
            f.write(f"{student_id},{grade.points},{grade.feedback}\n")


if __name__ == '__main__':
    grader: Grader = Grader(SETTINGS["submission_dir"],
                            SETTINGS["entry_point"],
                            SETTINGS["input_dir"],
                            SETTINGS["output_dir"],
                            SETTINGS["timeout"])
    grader.init()
    grader.run()
    write_grades(grader.extract())
