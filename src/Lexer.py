from tokens import *

ESCAPE_CHARS = "nrt\\'\""

line = 1
tokens = []

def err(msg, *args):
    raise Exception(msg % args)

def extract(begin, end):
    return begin[:end]

def parse_escape_chars(input_str):
    s = []
    i = 0
    while i < len(input_str):
        if input_str[i] == '\\':
            if i + 1 < len(input_str):
                if input_str[i + 1] == 'n':
                    s.append('\n')
                elif input_str[i + 1] == 'r':
                    s.append('\r')
                elif input_str[i + 1] == 't':
                    s.append('\t')
                else:
                    s.append(input_str[i+1])
            i += 2
            continue
        s.append(input_str[i])
        i += 1
    return ''.join(s)

class Token:
    def __init__(self, code, line):
        self.code:int = code
        self.line:int = line
        self.text:str = ""
        self.i:int = 0
        self.d:float = 0
        self.c:str = ""

    
def addTk(code):
    global tokens, line
    tk = Token(code, line)
    tokens.append(tk)
    return tk


def tokenize(pch):
    global tokens, line
    tokens = []
    line = 1
    i = 0
    length = len(pch)
    while True:
        if i >= length:
            addTk(END)
            break
        ch = pch[i]

        #delimiters
        if ch == ',':
            addTk(COMMA)
            i += 1
        elif ch == ';':
            addTk(SEMICOLON)
            i += 1
        elif ch == '(':
            addTk(LPAR)
            i += 1
        elif ch == ')':
            addTk(RPAR)
            i += 1
        elif ch == '[':
            addTk(LBRACKET)
            i += 1
        elif ch == ']':
            addTk(RBRACKET)
            i += 1
        elif ch == '{':
            addTk(LACC)
            i += 1
        elif ch == '}':
            addTk(RACC)
            i += 1
        elif ch == '\0':
            addTk(END)
            break

        #operators
        elif ch == '+':
            addTk(ADD)
            i += 1
        elif ch == '-':
            addTk(SUB)
            i += 1
        elif ch == '*':
            addTk(MUL)
            i += 1
        elif ch == '.':
            if i + 1 < length and (pch[i+1].isalpha() or pch[i+1] == "_" ):
                addTk(DOT)
                i += 1
            else: 
                err("Invalid operator on line %d: '%c' (ASCII: %d)\nExpected an identifier after DOT operator", line, ch, ord(ch))
        elif ch == '/':
            if i+1 < length and pch[i+1] == '/':
                i += 2
                while i < length and pch[i] not in '\r\n\0':
                    i += 1
            elif i+1 < length and pch[i+1] == '*':
                i += 2
                comment_line = line
                while i+1 < length:
                    if pch[i] == '*' and pch[i+1] == '/':
                        i += 2
                        break
                    elif pch[i] == '\n':
                        line += 1
                        i += 1
                    elif pch[i] == '\r':
                        if i+1 < length and pch[i+1] == '\n':
                            i += 1
                        line += 1
                        i += 1
                    else:
                        i += 1
                else:
                    err("Unterminated comment starting at line %d", comment_line)
            else: 
                addTk(DIV)
                i += 1
        elif ch == '!':
            if i+1 < length and pch[i+1] == '=':
                addTk(NOTEQ)
                i += 2
            else:
                addTk(NOT)
                i += 1
        elif ch == '&':
            if i+1 < length and pch[i+1] == '&':
                addTk(AND)
                i += 2
            else:
                err("Invalid operator on line %d: '%c' (ASCII: %d)\nExpected a second '%c'", line, ch, ord(ch), ch)
        elif ch == '|':
            if i+1 < length and pch[i+1] == '|':
                addTk(OR)
                i += 2
            else:
                err("Invalid operator on line %d: '%c' (ASCII: %d)\nExpected a second '%c'", line, ch, ord(ch), ch)
        elif ch == '=':
            if i+1 < length and pch[i+1] == '=':
                addTk(EQUAL)
                i += 2
            else:
                addTk(ASSIGN)
                i += 1
        elif ch == '<':
            if i+1 < length and pch[i+1] == '=':
                addTk(LESSEQ)
                i += 2
            else:
                addTk(LESS)
                i += 1
        elif ch == '>':
            if i+1 < length and pch[i+1] == '=':
                addTk(GREATEREQ)
                i += 2
            else:
                addTk(GREATER)
                i += 1

        #whitespace
        elif ch == '\r':
            if i +1 < length and pch[i+1] == '\n':
                i += 1
            i += 1
            line += 1
        elif ch == '\n':
            i += 1
            line += 1
        elif ch == '\t' or ch == ' ':
            i+= 1

        #identifiers n keywordz
        elif ch.isalpha() or ch == '_':
            start = i
            i += 1
            while i < length and (pch[i].isalnum() or pch[i] == '_'):
                i += 1
            text = pch[start:i]
            if text == "int":
                addTk(TYPE_INT)
            elif text == "char":
                addTk(TYPE_CHAR) 
            elif text == "double":
                addTk(TYPE_DOUBLE) 
            elif text == "if":
                addTk(IF)
            elif text == "else":
                addTk(ELSE)
            elif text == "while":
                addTk(WHILE)
            elif text == "void":
                addTk(VOID)
            elif text == "return":
                addTk(RETURN)
            elif text == "struct":
                addTk(STRUCT)
            else:
                tk = addTk(ID)
                tk.text = text
            
        #numbers (hex, octal, decimal, double)
        elif ch.isdigit() or (ch == '0' and i+1 < length and pch[i+1].lower() == 'x'):
            start = i
            # Hexadecimal
            if ch == '0' and i+1 < length and pch[i+1].lower() == 'x':
                i += 2  # Skip '0x'
                hex_start = i
                while i < length and (pch[i].isdigit() or pch[i].lower() in 'abcdef'):
                    i += 1
                if i == hex_start:
                    text = pch[start:i]
                    err("Invalid hexadecimal constant on line %d: %s", line, text)
                text = pch[start:i]
                tk = addTk(INT)
                tk.i = int(text, 16)
            else:
                # Decimal or octal
                i += 1
                while i < length and pch[i].isdigit():
                    i += 1
                # Double
                if i < length and (pch[i] == '.' or pch[i] in 'eE'):
                    num_digits = 0
                    if i < length and pch[i] == '.':
                        i += 1
                        frac_start = i
                        while i < length and pch[i].isdigit():
                            i += 1
                            num_digits += 1
                        if num_digits == 0 and (i >= length or pch[i].lower() != 'e'):
                            text = pch[start:i]
                            err("invald double constant on line %d: %s", line, text)
                    if i < length and pch[i] in 'eE':
                        i+= 1
                        if i < length and pch[i] in '+-':
                            i += 1
                        num_digits = 0
                        exp_start = i
                        while i < length and pch[i].isdigit():
                            i += 1
                            num_digits += 1
                        if num_digits == 0:
                            text = pch[start:i]
                            err("Invalid double constatnt on line %d: %s", line, text)
                    text = pch[start:i]
                    tk = addTk(DOUBLE)
                    tk.d = float(text)
                else:
                    text = pch[start:i]
                    tk = addTk(INT)
                    # Octal
                    if text.startswith('0') and len(text) > 1:
                        for c in text[1:]:
                            if not ('0' <= c <= '7'):
                                err("Invalid octal constant on line %d: %s", line, text)
                        tk.i = int(text, 8)
                    else:
                        tk.i = int(text)
        
        #char constant
        elif ch == "'":
            start = i
            i += 1
            if i < length and pch[i] == '\\' and i+2 < length and pch[i+2] == "'" and pch[i+1] in ESCAPE_CHARS:
                tk = addTk(CHAR)
                if pch[i+1] == 'n':
                    tk.c = '\n'
                elif pch[i+1] == 'r':
                    tk.c = '\r' 
                elif pch[i+1] == 't':
                    tk.c = '\t'
                else:
                    tk.c = pch[i+1]
                i += 3
            elif i < length and pch[i] != '\\' and i+1 < length and pch[i+1] == "'":
                tk = addTk(CHAR)
                tk.c = pch[i]
                i += 2
            else:
                while i < length and pch[i] not in '\n\r\0':
                    i += 1
                text = pch[start:i]
                err("Invalid character constant on line %d: %s", line, text)

        #string const
        elif ch == '"':
            start = i + 1
            i += 1
            while i < length and pch[i] != '"' and pch[i] not in '\n\r\0':
                if pch[i] == '\\' and i+1 < length and pch[i+1] == '"':
                    i += 2
                elif pch[i] == '\\' and (i+1 >= length or pch[i+1] not in ESCAPE_CHARS):
                    text = pch[start-1:i+2]
                    err("Invalid string const on line %d: %s\nBad escape char", line, text)
                else:
                    i += 1
            if i < length and pch[i] == '"':
                tk = addTk(STRING)
                text = pch[start:i]
                tk.text = parse_escape_chars(text)
                i += 1
            else:
                text = pch[start-1:i]
                err("Invalid string constant on line %d: %s\nMissing end double-quote", line, text)
        else:
            err("Invalid character on line %d: '%c' (ASCII: %d)", line, ch, ord(ch))
    return tokens

def show_tokens(tokens, stream):
    print("LINE\tNAME:VALUE", file = stream)
    for tk in tokens:
        print(f"{tk.line}\t\t{get_token_name(tk.code)}", end = '', file = stream)
        if tk.code in (ID, STRING):
            print(f":{tk.text}", file = stream)
        elif tk.code == INT:
            print(f":{tk.i}", file = stream)
        elif tk.code == DOUBLE:
            print(f":{tk.d:.10f}", file = stream)
        elif tk.code == CHAR:
            if tk.c == '\n':
                print(":\\n", file = stream)
            elif tk.c == '\r':
                print(":\\r", file = stream)
            elif tk.c == '\t':
                print(":\\t", file = stream)
            else:
                print(f":{tk.c}", file = stream)
        else:
            print(file = stream)
    print(file = stream)

def free_tokens(tokens):
    tokens.clear()

def done():
    """Free all dynamically allocated memory"""
    global tokens
    free_tokens(tokens)
    tokens = []
