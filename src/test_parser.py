import sys
import os
from Lexer import tokenize, show_tokens
from parser import Parser  # Import the Parser class, not parse function

# Test cases for the parser
test_cases = [
    # Test case 1: Simple variable declaration
    {
        "name": "Simple variable declaration",
        "code": """
int x;
double y;
char c;
"""
    },
    
    # Test case 2: Main function from original example
    {
        "name": "Main function",
        "code": """
void main()
{
    int i, s;
    s = 10;
    put_i(s);
}
"""
    },

    # Test case 3: If-else statement
    {
        "name": "If-else statement",
        "code": """
int max(int a, int b)
{
    if (a > b)
        return a;
    else
        return b;
}
"""
    },
    
    # Test case 4: While loop
    {
        "name": "While loop",
        "code": """
int factorial(int n)
{
    int result;
    result = 1;
    while (n > 0) {
        result = result * n;
        n = n - 1;
    }
    return result;
}
"""
    },
    
    # Test case 5: Complex expressions
    {
        "name": "Complex expressions",
        "code": """
double calculate()
{
    double x, y, z;
    x = 3.14;
    y = 2.5 + x * 1.5;
    z = (x + y) / (x - y);
    return z;
}
"""
    },
    
    # Test case 6: Array declaration and usage
    {
        "name": "Array operations",
        "code": """
int sum_array()
{
    int arr[10];
    int i, sum;
    sum = 0;
    i = 0;
    while (i < 10) {
        sum = sum + arr[i];
        i = i + 1;
    }
    return sum;
}
"""
    },
    
    # Test case 7: Character operations
    {
        "name": "Character operations",
        "code": """
char get_grade(int score)
{
    char grade;
    if (score >= 90)
        grade = 'A';
    else if (score >= 80)
        grade = 'B';
    else
        grade = 'F';
    return grade;
}
"""
    },

    # Test case 8: Struct definition and usage
    {
        "name": "Struct definition",
        "code": """
struct Point {
    int x;
    int y;
};

void move_point()
{
    struct Point p;
    p.x = 10;
    p.y = 20;
}
"""
    },

    # Test case 9: Function with multiple parameters
    {
        "name": "Function with parameters",
        "code": """
int add(int a, int b, int c)
{
    return a + b + c;
}

void test()
{
    int result;
    result = add(1, 2, 3);
    put_i(result);
}
"""
    },

    # Test case 10: Error case - syntax error
    {
        "name": "Syntax Error Test",
        "code": """
int broken_function()
{
    int x
    return x;  // Missing semicolon above
}
"""
    }
]

def test_parser():
    """Test the parser with various code examples"""
    print("=" * 60)
    print("PARSER TESTING")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Show source code
            print("Source Code:")
            print(test_case['code'])
            
            # Tokenize
            tokens = tokenize(test_case['code'])
            
            print("\nTokens:")
            show_tokens(tokens, sys.stdout)
            
            # Parse using your Parser class
            print("\nParsing...")
            parser = Parser(tokens)
            parser.parse()  # This should print "Syntax ok" if successful
            
            print("✓ Parsing successful!")
            passed_tests += 1
            
        except Exception as e:
            print(f"✗ Parsing failed: {e}")
            # Print more details for debugging
            if hasattr(e, '__traceback__'):
                import traceback
                print("Error details:")
                traceback.print_exc()
        
        print("-" * 40)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed")

def test_single_case(case_index):
    """Test a single test case by index (1-based)"""
    if case_index < 1 or case_index > len(test_cases):
        print(f"Invalid test case index. Please use 1-{len(test_cases)}")
        return
    
    test_case = test_cases[case_index - 1]
    print(f"Testing: {test_case['name']}")
    print("-" * 40)
    
    try:
        tokens = tokenize(test_case['code'])
        parser = Parser(tokens)
        parser.parse()
        print("✓ Test passed!")
    except Exception as e:
        print(f"✗ Test failed: {e}")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        try:
            case_num = int(sys.argv[1])
            test_single_case(case_num)
        except ValueError:
            print("Usage: python test_parser.py [test_case_number]")
            print(f"Available test cases: 1-{len(test_cases)}")
    else:
        # Run all tests
        test_parser()
    
    print("\nTesting complete!")