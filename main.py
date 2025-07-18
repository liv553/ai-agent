import os
import json
from dotenv import load_dotenv
from google import genai
import sys

# Importa as funções REAIS que vamos executar
from functions.get_files_info import get_files_info, get_file_content, write_file
from functions.run_python import run_python_file

def main():
    print("Hello from ai-agent!")
    load_dotenv()

    args = sys.argv[1:]
    is_verbose = "--verbose" in args
    if is_verbose:
        args.remove("--verbose")
    
    if not args:
        print("No question provided. Exiting program.")
        sys.exit(1)
    question = " ".join(args)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # --- PROMPT MESTRE COM ESTRATÉGIA DE DEPURAÇÃO ---
    system_prompt = """
You are an expert AI coding agent. Your goal is to solve the user's request by calling the available functions in sequence.

**PLANNING:**
1.  **Explore:** First, use the `get_files_info` function to see the project structure. Start at the root (`.`) and then explore subdirectories if necessary.
2.  **Read & Analyze:** After you know the file structure, use `get_file_content` to read the files that seem relevant to the task.
3.  **Propose a Fix:** Once you understand the code, decide what changes are needed. Use `write_file` to apply the fix to the correct file.
4.  **Test:** Use `run_python_file` to execute tests or the main application to ensure your fix worked correctly.
5.  **Final Answer:** When the task is complete and verified, provide a final answer in plain text.

**RESPONSE FORMAT:**
- On each turn, you must respond with ONLY a single JSON object representing the next function call from your plan.
- Do not add any other text, explanations, or markdown.
- The format for a function call MUST BE: `{"function_name": "...", "args": {"...": "..."}}`

**AVAILABLE FUNCTIONS and their arguments:**
- `get_files_info(directory: str)`
- `get_file_content(file_path: str)`
- `write_file(file_path: str, content: str)`
- `run_python_file(file_path: str, args: list[str])`
"""
    
    initial_prompt = f"{system_prompt}\n\nUSER'S REQUEST: \"{question}\""
    
    conversation_history = [initial_prompt]
    model_name = "models/gemini-1.5-flash"
    
    available_functions_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file": write_file,
        "run_python_file": run_python_file,
    }

    # Inicia o loop do agente
    for i in range(20):
        print(f"\n--- Iteration {i + 1} ---")
        
        response = client.models.generate_content(
            model=model_name,
            contents=conversation_history
        )
        
        if not response.candidates:
            print("No response from model. Exiting loop.")
            break
            
        response_text = response.text.strip()
        conversation_history.append(response_text)

        if response_text.startswith("```json"):
            clean_json_string = response_text.strip("```json\n").strip("```").strip()
        else:
            clean_json_string = response_text
        
        try:
            data = json.loads(clean_json_string)
            if "function_name" in data and "args" in data:
                function_name = data["function_name"]
                function_args = data.get("args", {})
                
                if is_verbose:
                    print(f"Calling function: {function_name}({function_args})")
                else:
                    print(f" - Calling function: {function_name}")
                
                if function_name in available_functions_map:
                    function_to_call = available_functions_map[function_name]
                    function_args["working_directory"] = "./calculator"
                    result = function_to_call(**function_args)
                    tool_feedback = f"FUNCTION RESULT:\n{result}\n"
                    conversation_history.append(tool_feedback)
                    
                    if is_verbose:
                        print(f"-> {result}")
                else:
                    tool_feedback = f"FUNCTION RESULT:\nError: Unknown function '{function_name}'.\n"
                    conversation_history.append(tool_feedback)
            else:
                print(f"\nFinal response:\n{clean_json_string}")
                break
        except (json.JSONDecodeError, TypeError):
            print(f"\nFinal response:\n{response_text}")
            break
    else:
        print("\nMax iterations reached.")


if __name__ == "__main__":
    main()