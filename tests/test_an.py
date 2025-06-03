import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from Lexer import tokenize
from parser import Parser

# This code has duplicate struct and variable names to trigger name analysis errors
source_code = """
int isdigit(char ch)
{
	return ch>='0'&&ch<='9';
}

void main()
{
	char		c;
	put_s("c=");
	c=get_c();
	put_i(isdigit(c));
}
"""

tokens = tokenize(source_code)
parser = Parser(tokens)
try:
    parser.parse()
    print("Name analysis ok (unexpected)")
except Exception as e:
    print("Name analysis error detected:", e)