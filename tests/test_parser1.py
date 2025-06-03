import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from Lexer import tokenize
from parser import Parser

source_code = """
/*** primul *** program ***/
void main()
{
	put_s("salut");
}
//sfarsit
"""

tokens = tokenize(source_code)
parser = Parser(tokens)
try:
    parser.parse()
    print("Syntax ok")
except Exception as e:
    print("Syntax error:", e)