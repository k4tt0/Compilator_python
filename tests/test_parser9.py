import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from Lexer import tokenize
from parser import Parser

source_code = """
struct Pt{
    int x,y;
};

struct Pt points[20/4+5];

int count()
{
    int i,n;
    for(i=n=0;i<10;i=i+1){
        if(points[i].x>=0&&points[i].y>=0)n=n+1;
    }
    return n;
}

void main()
{
    put_i(count());
}
"""

tokens = tokenize(source_code)
parser = Parser(tokens)
try:
    parser.parse()
    print("Syntax ok")
except Exception as e:
    print("Syntax error:", e)