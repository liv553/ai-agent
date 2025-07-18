import os
import subprocess
from google.genai import types

from .get_files_info import _validate_path

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file with optional arguments.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to be executed, relative to the working directory."
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="A list of string arguments to pass to the Python script."
            ),
        },
        required=["file_path"]
    ),
)

def run_python_file(working_directory, file_path, args =[]):
    validated_path, error = _validate_path(working_directory, file_path)

    if error:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(validated_path):
        return f'Error: File "{file_path}" not found'
    
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        command = ["python", validated_path] + args

        completed_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            cwd= working_directory
        )

        output_parts = []

        if completed_process.returncode != 0:
            output_parts.append(f"Process exited with code {completed_process.returncode}")

        if completed_process.stdout:
            output_parts.append(f"STDOUT:\n{completed_process.stdout.strip()}")

        if completed_process.stderr:
            output_parts.append(f"STDERR:\n{completed_process.stderr.strip()}")
        
        if not output_parts:
            return "No output produced."
        
        return "\n\n".join(output_parts)
    
    except subprocess.TimeoutExpired:
        return f"Error: Execution of '{file_path}' timed out after 30 seconds."
    except Exception as e:
        return f"Error: executing Python file: {e}"