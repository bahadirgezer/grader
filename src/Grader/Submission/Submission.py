import os
import shutil
import zipfile

from typing import List


class Submission:
    def __init__(self, submission_path: str):
        self.submission_path = submission_path
        self.valid: bool = None
        self.points = 0
        self.student_id: str = self.get_student_id()
        self.clear()
        self.unzip()

        print(self.student_id)
        print(self.submission_path + "\n")

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
