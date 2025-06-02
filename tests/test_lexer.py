import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from Lexer import tokenize, show_tokens

source_code = """
int sum()
{
    int  i,v[5],s;
    s=0;
    for(i=0;i<5;i=i+1){
        v[i]=i;
        s=s+v[i];
    }
    return s;
}

void main()
{
    int  i,s;
    for(i=0;i<1000000;i=i+1)
        s=sum();
    put_i(s);
}
"""

tokens = tokenize(source_code)
show_tokens(tokens, stream=None)  # stream=None prints to stdoutimport sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))