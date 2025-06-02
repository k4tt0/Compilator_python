# AtomC/C Compiler (Python)
## Overview

AtomC/C is a compiler for a C-like language, implemented in Python. It features a recursive descent parser, a symbol table, and a type system. The project is organized for clarity and extensibility, with error handling via exceptions.

## Features

- Lexical analysis for identifiers, keywords, constants, delimiters, operators, and whitespace.
- Parsing of C-like syntax including structs, functions, variables, and expressions.
- Domain and type analysis to ensure semantic correctness.
- Modular codebase with separate files for parsing, symbol tables, and type analysis.

## Lexical Rules

- **Identifiers**
- **Keywords**
- **Constants**
- **Delimiters**
- **Operators**
- **Whitespace** (ignored)

## Syntax Rules

```
unit: ( structDef | fnDef | varDef )* END

structDef: STRUCT ID LACC varDef* RACC SEMICOLON

varDef: typeBase ID arrayDecl? SEMICOLON

typeBase: TYPE_INT | TYPE_DOUBLE | TYPE_CHAR | STRUCT ID

arrayDecl: LBRACKET INT? RBRACKET

fnDef: ( typeBase | VOID ) ID
    LPAR ( fnParam ( COMMA fnParam )* )? RPAR
    stmCompound

fnParam: typeBase ID arrayDecl?

stm: stmCompound
    | IF LPAR expr RPAR stm ( ELSE stm )?
    | WHILE LPAR expr RPAR stm
    | RETURN expr? SEMICOLON
    | expr? SEMICOLON

stmCompound: LACC ( varDef | stm )* RACC

expr: exprAssign

exprAssign: exprUnary ASSIGN exprAssign | exprOr

exprOr: exprOr OR exprAnd | exprAnd

exprAnd: exprAnd AND exprEq | exprEq

exprEq: exprEq ( EQUAL | NOTEQ ) exprRel | exprRel

exprRel: exprRel ( LESS | LESSEQ | GREATER | GREATEREQ ) exprAdd | exprAdd

exprAdd: exprAdd ( ADD | SUB ) exprMul | exprMul

exprMul: exprMul ( MUL | DIV ) exprCast | exprCast

exprCast: LPAR typeBase arrayDecl? RPAR exprCast | exprUnary

exprUnary: ( SUB | NOT ) exprUnary | exprPostfix

exprPostfix: exprPostfix LBRACKET expr RBRACKET
       | exprPostfix DOT ID
       | exprPrimary

exprPrimary: ID ( LPAR ( expr ( COMMA expr )* )? RPAR )?
       | INT | DOUBLE | CHAR | STRING | LPAR expr RPAR
```

## Domain and Type Analysis

- **structDef:** Struct names must be unique in their domain. Struct members must have unique names.
- **varDef:** Variable names must be unique in their domain. Arrays must have a specified dimension.
- **typeBase:** Struct types must be previously defined.
- **fnDef:** Function names must be unique in their domain. Each function has its own local domain.
- **fnParam:** Parameter names must be unique. Array parameters lose their dimension.
- **stm:**
  - if/while conditions must be scalar.
  - return expressions must be scalar and convertible to the function's return type.
- **exprAssign:**
  - Left side must be a left-value, not a constant, and both sides must be scalar and convertible.
- **exprOr/And/Eq/Rel/Add/Mul:**
  - Both operands must be scalar and not structs. Result is usually int or the appropriate type.
- **exprCast:**
  - Structs cannot be cast. Arrays can only be cast to arrays, scalars to scalars.
- **exprPostfix:**
  - Only arrays can be indexed. Only structs can use the dot operator. Fields must exist.
- **exprPrimary:**
  - Identifiers must exist. Only functions can be called, and argument types must match parameter types.

## Notes

- The parser is implemented as a recursive descent parser in Python.
- The symbol table and type system are managed in `ad.py` and `at.py`.
- Error handling is performed with exceptions and descriptive messages.