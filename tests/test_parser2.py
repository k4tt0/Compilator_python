import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from Lexer import tokenize
from parser import Parser
from ad import Type, Symbol, Domain, symTable, pushDomain, dropDomain
from at import Ret, CtVal, canBeScalar, convTo, cast, getArithType
from tokens import *

def test_domain_analysis():
    print("\nTesting Domain Analysis...")
    
    # Test struct redefinition
    source = """
    struct Point1 { int x; int y; };
    struct Point1 { int z; };  // Should fail - redefinition
    """
    tokens = tokenize(source)
    parser = Parser(tokens)
    try:
        parser.parse()
        print("❌ Struct redefinition test failed (should raise error)")
    except Exception as e:
        print("✅ Struct redefinition correctly detected:", e)

    # Test variable scope
    source = """
    int x1;
    void test() {
        int x1;  // OK - different scope
        {
            int x1;  // OK - different scope
            double x1;  // Should fail - same scope
        }
    }
    """
    tokens = tokenize(source)
    parser = Parser(tokens)
    try:
        parser.parse()
        print("❌ Variable redefinition test failed (should raise error)")
    except Exception as e:
        print("✅ Variable redefinition correctly detected:", e)

def test_type_analysis():
    print("\nTesting Type Analysis...")
    
    # Test scalar type conversions
    t_int = Type(TB_INT)
    t_double = Type(TB_DOUBLE)
    t_char = Type(TB_CHAR)
    
    print("Testing type conversions...")
    # Allowed conversions
    print("✅ int -> double:", convTo(t_int, t_double))      # Should be True
    print("✅ char -> int:", convTo(t_char, t_int))          # Should be True
    # Disallowed conversions
    print("✅ double -> int:", not convTo(t_double, t_int))  # Should be False
    
    # Test array conversions
    t_int_arr = Type(TB_INT, None, 10)
    t_double_arr = Type(TB_DOUBLE, None, 10)
    print("✅ array conversions:", not convTo(t_int_arr, t_double_arr))
    print("✅ array to scalar:", not convTo(t_int_arr, t_int))

def test_complex_program():
    print("\nTesting Complex Program...")
    
    source = """
    struct Point2 {
        int x2;
        int y2;
    };
    
    double calc2(double a2, double b2) {
        double result2;
        result2 = a2 + b2;
        return result2;
    }
    
    void main2() {
        struct Point2 p2;
        int arr2[10];
        double d2;
        
        p2.x2 = 10;
        arr2[0] = 20;
        d2 = 3.14;
        
        d2 = calc2(arr2[0], d2);
    }
    """
    
    tokens = tokenize(source)
    parser = Parser(tokens)
    try:
        parser.parse()
        print("✅ Complex program analysis passed")
    except Exception as e:
        print("❌ Complex program analysis failed:", e)

if __name__ == "__main__":
    test_domain_analysis()
    test_type_analysis()
    test_complex_program()