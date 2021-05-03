# CodeGen
CodeGen is a tool for generating python code using python code(🧠🧠🧠). This is useful for projects like [SchemaGen](https://github.com/GoZaddy/SchemaGen) where you need to generate code based on certain input.

# Usage
Here's a sample of how CodeGen works:

Input: 
```python
from codegen import CodegenTool, If, IfElse, Expr, String
codegen = CodegenTool('test.py')
ie = IfElse(
    if_=If(
        expr=Expr(f"{String('a')} != {String('b')}"),
        action=[Expr("print('true')")]
    ),
    else_action=[Expr("print('else')")]
)
ie.add_elif(
    If(
        expr=Expr(f"{String('a')} == {String('b')}"),
        action=[Expr("print('false')")],
        if_type='elif'
    )
) 
codegen.write_if_else(ie)
```

Output:
```python
# This file was generated by CodegenTool
if 'a' != 'b':
    print('true')
elif 'a' == 'b':
    print('false')
else:
    print('else')
```

# Contributing
I'm currently busy with life et al and would really appreciate contributions to codegen.

# Other Notes:
I'm also looking for another name for this project