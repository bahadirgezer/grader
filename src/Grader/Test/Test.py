
class Test:
    def __init__(self, name, input_path, output_path):
        self.name: str = name
        self.input_path: str = input_path
        self.output_path: str = output_path

    def grade(self, generated_output_path):
        pass