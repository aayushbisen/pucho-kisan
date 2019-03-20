import os
import uuid


def question_file_path(question_file, filepath):

    filename, file_extension = os.path.splitext(filepath)
    filename = str(uuid.uuid4())

    return f'questions/{filename}{file_extension}'
