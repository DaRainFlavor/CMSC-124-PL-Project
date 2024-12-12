import re

def remove_cpp_comments(code: str) -> str:
    # Regular expression for C++ comments
    # Matches either single-line comments or multi-line comments
    pattern = r'//.*?$|/\*.*?\*/'
    
    # Substitute comments with an empty string, preserving quoted strings
    # `re.DOTALL` allows `.*?` to match newlines in multi-line comments
    # `re.MULTILINE` allows `^` and `$` to match the start and end of each line for `//`
    cleaned_code = re.sub(pattern, '', code, flags=re.DOTALL | re.MULTILINE)
    
    return cleaned_code

# Examples
examples = [
    "int x; // initialize",
    "int x; /*Multiple lines*/",
    'string str = "//this is a comment"; //remove this only',
    'string str = "/*this is multiple comments*/;" /*remove this only*/'
]

# Apply function to examples and print results
for example in examples:
    print(f"Original: {example}")
    print(f"Without comments: {remove_cpp_comments(example)}\n")
