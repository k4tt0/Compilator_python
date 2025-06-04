import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from Lexer import tokenize, show_tokens

source_code = """
/*
testare analizor lexical
*/
void main()
{
	if(0xc==014)put_s("\"egal\"\t\t(h,o)");
		else put_s("\"inegal\"\t\t(h,o)");
	if(20E-1==2.0&&0.2e+1==0x2)put_c('=');  // 2 scris in diverse feluri
		else put_c('\\\\');
}
"""

tokens = tokenize(source_code)
show_tokens(tokens, stream=None)  # stream=None prints to stdoutimport sys