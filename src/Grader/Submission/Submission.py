import os
import re
import shutil
import subprocess
import zipfile
from subprocess import Popen, PIPE

from typing import List


class Submission:
    def __init__(self, submission_path: str, entry_point: str):
        self.points: int = 0
        self.valid: bool = None
        self.entry_point = entry_point
        self.submission_path = submission_path
        self.feedback: dict = dict()
        self.student_id: str = self.get_student_id()

    def ready(self) -> bool:
        self.clear()
        self.unzip()
        self.organize()
        return self.valid

    # find all files under submission_path, walk subdirectories
    def find_all_files(self) -> List[str]:
        files = []
        for root, dirs, file in os.walk(self.submission_path):
            for f in file:
                files.append(os.path.join(root, f))
        return files

    def find_files(self, file_extension: str) -> List[str]:
        files = []
        for file in os.listdir(self.submission_path):
            if file.endswith(file_extension):
                files.append(file)
        return files

    # student id is found in the filename of the submission .zip file. <student_id>.zip
    def get_student_id(self) -> str:
        zip_files: List[str] = self.find_files(".zip")
        if len(zip_files) == 1:
            self.valid = True
            return zip_files[0].replace(".zip", "")
        else:
            self.valid = False
            return "INVALID"

    def clear(self):
        if not self.valid:
            return
        for root, dirs, files in os.walk(self.submission_path):
            for f in files:
                if f.endswith(".zip"):
                    continue
                os.remove(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    def unzip(self):
        if not self.valid:
            return
        zip_files: List[str] = self.find_files(".zip")
        if len(zip_files) != 1:
            self.valid = False
            return
        zip_file_path = os.path.join(self.submission_path, zip_files[0])
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(self.submission_path)

        # if the submission directory contains a directory named __MACOSX, delete it
        macosx_dir = os.path.join(self.submission_path, "__MACOSX")
        if os.path.exists(macosx_dir):
            shutil.rmtree(macosx_dir)

    def organize(self):
        if not self.valid:
            return

        # create a directory named {submission_path}/grading
        grading_dir = os.path.join(self.submission_path, "grading")
        if not os.path.exists(grading_dir):
            os.mkdir(grading_dir)

        # find the entry point file
        entry_point_file = None
        entry_point_file_extension = self.entry_point.split(".")[-1]
        files: List[str] = self.find_all_files()
        for file in files:
            if file.endswith(self.entry_point):
                entry_point_file = file
                break
        if entry_point_file is None:
            self.valid = False
            return

        entry_point_dir = os.path.dirname(entry_point_file)
        for file in files:
            if file.endswith(entry_point_file_extension) and os.path.dirname(file) == entry_point_dir:
                shutil.move(file, grading_dir)

        # clear every file and subdirectory except for inside the grading directory, and the .zip files
        for root, dirs, files in os.walk(self.submission_path):
            for f in files:
                if f.endswith(".zip"):
                    continue
                if root != grading_dir:
                    os.remove(os.path.join(root, f))
            for d in dirs:
                if d != "grading":
                    shutil.rmtree(os.path.join(root, d))

    def compile(self):
        if not self.valid:
            return
        original_dir = os.getcwd()
        grading_dir = os.path.join(self.submission_path, "grading")
        os.chdir(grading_dir)
        if not os.path.exists("bin"):
            os.mkdir("bin")

        # compile the entry point file, and catch errors
        compile_command = "javac -d bin *.java"
        compile_process = Popen(compile_command, shell=True, stdout=PIPE, stderr=PIPE)
        compile_process.wait()
        self.valid = os.path.exists(os.path.join(grading_dir, "bin", self.entry_point.replace(".java", ".class")))
        os.chdir(original_dir)
        return

    def run(self, input_path: str, timeout: int = 5):
        case_name = os.path.basename(input_path).replace(".in", "")
        if not self.valid:
            return
        original_dir = os.getcwd()
        bin_dir = os.path.join(self.submission_path, "grading", "bin")
        os.chdir(bin_dir)
        entry_class = self.entry_point.replace(".java", "")
        output_path = os.path.join(self.submission_path, "output",
                                   os.path.basename(input_path).replace(".in", ".out"))
        try:
            subprocess.run(
                ["java", entry_class, input_path, output_path],
                stdout=PIPE, stderr=PIPE, timeout=timeout, check=True)
        except subprocess.CalledProcessError as failed:
            # parse the stderr output to identify the error
            error_msg = parse_stderr(failed.stderr.decode("utf-8"))
            self.feedback[case_name] = \
                f"Runtime Error: {error_msg}."
        except subprocess.TimeoutExpired:
            self.feedback[case_name] = \
                f"Timed out after 15 seconds."
        os.chdir(original_dir)
        return

    def compiled(self) -> bool:
        if not self.valid:
            return False
        grading_dir = os.path.join(self.submission_path, "grading")
        return os.path.exists(os.path.join(grading_dir, "bin", self.entry_point.replace(".java", ".class")))

    # check if the source code contains any java.util.LinkedList, java.util.ArrayList imports
    def check_for_illegal_imports(self) -> bool:
        for file in self.find_files(".java"):
            with open(file, "r") as f:
                for line in f:
                    if "import java.util.LinkedList" in line or "import java.util.ArrayList" in line:
                        return True
        return False


def parse_stderr(stderr: str) -> str:
    # Search for common error patterns in the output
    match = re.search(r'(?<=Exception: ).*', stderr)
    if match:
        return match.group(0)  # Return the matched exception message

    match = re.search(r'(?<=error: ).*', stderr)
    if match:
        return match.group(0)  # Return the matched error message

    match = re.search(r'(?<=Exception in thread ").*(?=")', stderr)
    if match:
        thread_name = match.group(0)  # Extract the thread name
        # Return a custom error message with the thread name and some details
        return f"Runtime error in thread {thread_name}: check the stderr output for more details"

    return "Unknown error"  # Return a default error message
