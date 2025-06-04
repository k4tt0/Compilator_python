import sys
import os
import subprocess
import tempfile

# Path to your src directory
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))

def run_test():
    # Create a temporary file with a minimal test
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(f'''
import sys
import os
sys.path.insert(0, r"{SRC_PATH}")

from Lexer import tokenize
from parser import Parser
from ad import symTable, addExtFn, addFnParam, Type
from tokens import TB_VOID, TB_INT

def init_symbol_table():
    s = addExtFn("put_i", None, Type(TB_VOID))
    addFnParam(s, "i", Type(TB_INT))

# Initialize symbol table
init_symbol_table()

# Very simple test case
code = """
void main()
{{
    int x;
}}
"""
tokens = tokenize(code)
parser = Parser(tokens)
parser.parse()
print("PASS: Test passed!")
''')
        temp_file = f.name

    # Run the test in a separate process
    print("\n--- Testing Simple Case ---")
    result = subprocess.run([sys.executable, temp_file], 
                           capture_output=True, text=True)
    
    # Print result
    if result.stdout.strip():
        print(f"STDOUT: {result.stdout.strip()}")
    if result.stderr.strip():
        print(f"STDERR: {result.stderr.strip()}")

if __name__ == "__main__":
    run_test()