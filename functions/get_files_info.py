import os
from config import MAX_FILE_CHARS
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the entire content of a specified file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be read, relative to the working directory."
            ),
        },
        required=["file_path"]
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specified file, creating it if it doesn't exist or overwriting it if it does.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be written, relative to the working directory."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file."
            ),
        },
        required=["file_path", "content"]
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

def _validate_path(working_directory, path_to_check):
    try:
        if not path_to_check:
            path_to_check = "."

        target_path = os.path.join(working_directory, path_to_check)

        real_working_dir = os.path.realpath(working_directory)
        real_target_path = os.path.realpath(target_path)

        if not real_target_path.startswith(real_working_dir):
            return None, f"Error: Cannot access '{path_to_check}' as it is outside the permitted working directory"

        return real_target_path, None
    except FileNotFoundError:
        return None, f"Error: Path '{path_to_check}' not found."
    except Exception as e:
        return None, f"Error: {e}"


def get_files_info(working_directory, directory=None):

    validated_path, error = _validate_path(working_directory, directory)

    if error:
        return error

    if not os.path.isdir(validated_path):
        return f'Error: "{directory}" is not a directory'

    try:        
        output_lines = []
        for item_name in os.listdir(validated_path):
            item_path = os.path.join(validated_path, item_name)
            file_size = os.path.getsize(item_path)
            is_dir = os.path.isdir(item_path)
            output_lines.append(f"- {item_name}: file_size={file_size} bytes, is_dir={is_dir}")

        return "\n".join(output_lines)
    except Exception as e:
        return f"Error: {e}"


def get_file_content(working_directory, file_path):
    validated_path, error = _validate_path(working_directory, file_path)
    if error:
        return error
    if not os.path.isfile(validated_path):
        return f'Error: "{file_path}" is not a file.'

    try:
        with open(validated_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
    

def write_file(working_directory, file_path, content):

    dir_name = os.path.dirname(file_path)

    validated_dir_path, error = _validate_path(working_directory, dir_name)
    
    if error:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'


    full_safe_path = os.path.join(validated_dir_path, os.path.basename(file_path))

    try:
        os.makedirs(os.path.dirname(full_safe_path), exist_ok=True)

        with open(full_safe_path, "w", encoding='utf-8') as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    
    except Exception as e:
        return f"Error: {e}"
