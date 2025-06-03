import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from Lexer import tokenize
from parser import Parser

source_code = """
void main()
{
	if(0xc==014)put_s("\"egal\"\t\t(h,o)");
		else put_s("\"inegal\"\t\t(h,o)");
	if(20E-1==2.0&&0.2e+1==0x2)put_c('=');  // 2 scris in diverse feluri
		else put_c('\\');
}
"""

tokens = tokenize(source_code)
parser = Parser(tokens)
try:
    parser.parse()
    print("Type analysis ok")
except Exception as e:
    print("Type analysis error detected:", e)