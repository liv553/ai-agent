from functions.get_files_info import get_files_info
from functions.get_files_info import get_files_content
from functions.get_files_info import write_file
from functions.run_python import run_python_file


if __name__ == "__main__":
    # print("--- Reading calculator/main.py ---")
    # result1 = get_files_content("calculator", "main.py")
    # print(result1)

    # print("\n--- Reading calculator/pkg/calculator.py ---")
    # result2 = get_files_content("calculator", "pkg/calculator.py")
    # print(result2)

    # print("\n--- Attempting to read /bin/cat ---")
    # result3 = get_files_content("calculator", "/bin/cat")
    # print(result3)

    # print("\n--- Attempting to read a non-existent file ---")
    # result4 = get_files_content("calculator", "pkg/does_not_exist.py")
    # print(result4)

    # print("\n--- Testing truncation with lorem.txt ---")
    # result5 = get_files_content("calculator", "lorem.txt")
    # print(result5)

    print("Testing write file")
    result6 = write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
    print(result6)

    print("Testing write file")
    result7 = write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
    print(result7)

    print("Testing write file")
    result8 = write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
    print(result8)

    print("--- Testing run python ---")
    result9 = run_python_file("calculator", "main.py", ["3 + 5"])
    print(result9)

    print("--- Testing run python ---")
    result10 = run_python_file("calculator", "tests.py")
    print(result10)

    print("--- Testing run python ---")
    result11 = run_python_file("calculator", "../main.py")
    print(result11)

    print("--- Testing run python ---")
    result11 = run_python_file("calculator", "nonexistent.py")
    print(result11)

    