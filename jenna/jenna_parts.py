from typing import List
from .utils import stringify, triple_stringify
from .errors import CodegenError


class Block:
    """
    Block is an 'interface' that represents a block of code. It is mostly used for indenting
    """

    def __init__(self, indent_level):
        self.indent_level = indent_level

    def set_indent_level(self, indent_level: int):
        self.indent_level = indent_level

    def get_indent_level(self) -> int:
        return self.indent_level

    def increment_indent_level(self):
        self.indent_level = self.indent_level + 1

    def __str__(self):
        pass


# The String type is used to differentiate between regular strings and strings that represent code
class String:
    def __init__(self, string):
        self.value = string

    def __str__(self):
        return stringify(self.value)


class Expr(Block):
    """
    This simple class represents a python expression e.g: a < b
    """

    def __init__(self, expression: str, indent_level=0):
        self.expression = expression
        super().__init__(indent_level)

    def __str__(self):
        tabs = '\t' * self.indent_level
        return tabs + self.expression


class Function(Block):
    """
    Function represents a python function

    Attributes:
        name: name of function
        arguments: arguments the function takes
        body: function body
        indent_level: indent level of the function
        decorators: list of decorators of the function
    """

    def __init__(self, name: str, arguments: list[str], body: List[Block] = None, indent_level=0,
                 decorators: List[str] = None):
        """
        This is used to initialise a Function object
        Args:
            name: name of the function
            arguments: arguments that the function take
            indent_level: indent level of the function
            decorators: decorators applied to the function. Each decorator should be in the form '@<decorator_name>'
        """
        self.name = name
        self.arguments = arguments
        if decorators is None:
            decorators = []
        self.decorators = decorators
        self.body = body
        super().__init__(indent_level)

    def __str__(self):
        args = ""
        if len(self.arguments) != 0:
            args = ', '.join(self.arguments)
        tabs = '\t' * self.get_indent_level()
        decorators = ''
        for i in self.decorators:
            decorators = decorators + f"\n{tabs}{i}"

        if self.body is None:
            return f"{decorators}\n{tabs}def {self.name}({args}):\n{tabs}\t# write method body\n{tabs}\tpass"
        else:
            body_lines = ''
            for block in self.body:
                block.set_indent_level(self.get_indent_level() + 1)
                if isinstance(block, Expr):
                    body_lines = body_lines + '\n' + str(block)
                    continue
                body_lines = body_lines + str(block)

            return f"{decorators}\n{tabs}def {self.name}({args}):{body_lines}"

    def add_decorator(self, decorator: str):
        """
        This adds a decorator to the Function object
        Args:
            decorator: a string containing the decorator, should begin with '@'

        """
        if decorator[0] != '@':
            raise CodegenError('Invalid decorator value. Decorator should start with @')
        else:
            self.decorators.append(decorator)

    def set_body(self, body: List[Block]):
        """
        This sets the function body
        Args:
            body: a list of Block objects that represent the new Function body

        """
        self.body = body


class Method(Function):
    """
    This presents a python method

    Attributes:
        name: name of method
        arguments: arguments the method takes
        body: function body
        indent_level: indent level of the method
        decorators: list of decorators of the method
        is_static: this should be True when the method is a static method

    """

    def __init__(self, name: str, arguments: list[str], indent_level=1, decorators: List[str] = None,
                 body: List[Block] = None, is_static: bool = False):
        if not is_static:
            arguments = ['self'] + arguments
        super().__init__(name, arguments, indent_level=indent_level, decorators=decorators, body=body)


class Class(Block):
    """
    This represents a python class

    Attributes:
        name: name of the class
        base_class: name of the class that this class inherits from(if any)
        add_init_method: this should be true if you want the class to have an init method
        indent_level: indent level of class
        description: description of the class
    """

    def __init__(self, name: str, base_class: str = None, add_init_method: bool = False, indent_level=0,
                 description: str = None):
        self.name = name[0].upper() + name[1:]
        self.base_class = base_class
        self.add_init_method = add_init_method
        self.methods = []
        self.class_variables = {}
        self.subclasses = []
        self.description = description
        super().__init__(indent_level)

    def __str__(self):
        class_def = ""
        init = ""
        methods = ""
        class_vars = ""
        subclasses = ""

        description = ''
        if self.description != '':
            description = '\n\t' + self.description

        # get tabs for indenting
        tabs = '\t' * self.get_indent_level()
        if self.base_class is None:
            class_def = f"\n\n{tabs}class {self.name}:{description}"
        else:
            class_def = f"\n\n{tabs}class {self.name}({self.base_class}):{description}"

        if self.add_init_method is True:
            init = f"\n\t{tabs}def __init__(self):\n\t\t{tabs}# initialise class here\n\t\tpass"

        for method in self.methods:
            methods = methods + f"\n{str(method)}"

        for var in self.class_variables:
            class_vars = class_vars + "\n\t" + tabs + var + " = " + self.class_variables[var]

        for subclass in self.subclasses:
            subclasses = "\t" + str(subclass)

        if subclasses or class_vars or init or methods:
            return f"{class_def}{subclasses}{class_vars}{init}{methods}\n"
        else:
            pass_expr = Expr('pass', indent_level=1)
            return f"{class_def}\n{str(pass_expr)}\n"

    def add_method(self, method_name: str = None, arguments_names: list[str] = None, decorators: List[str] = None,
                   method: Method = None):
        if method is not None:
            method.indent_level = self.get_indent_level() + 1
            self.methods.append(method)
        else:
            if method_name is None or arguments_names is None:
                raise CodegenError('method name or argument name invalid')
            self.methods.append(Method(name=method_name, arguments=arguments_names, decorators=decorators,
                                       indent_level=self.get_indent_level() + 1))

    def add_class_variable(self, variable_name, variable_value):
        value = str(variable_value)
        self.class_variables[variable_name] = value

    def add_sub_class(self, _class):
        # increase the subclass indent by 1 greater than the parent class' indent
        _class.set_indent_level(self.get_indent_level() + 1)
        self.subclasses.append(_class)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description: str):
        if description is None:
            self._description = ''
        else:
            self._description = triple_stringify(description)


class Variable:
    """
    This represents a python variable

    Attributes:
        name: name of the variable
        value: value of the variable
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        if isinstance(self.value, String) or isinstance(self.value, ClassInstance):
            value = str(self.value)
        else:
            value = self.value
        return "\n" + self.name + " = " + value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class ClassInstance:
    """
    This presents the creation of a class instance in python

    Attributes:
        class_name: the name of the class
        *args: the args passed to the class' init method
        **kwargs: the kwargs passed to the class' init method
    """

    def __init__(self, class_name: str, *args, **kwargs):
        """
        Create a ClassInstance object
        Args:
            class_name: the name of the class
            *args: the args passed to the class' init method
            **kwargs: the kwargs passed to the class' init method
        """
        self.class_name = class_name
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        args = ', '
        kwargs = []

        args = ', '.join(self.args)

        for kwarg in self.kwargs:
            val = self.kwargs[kwarg]
            if isinstance(val, String):
                val = str(val)
            kwargs.append(f"{kwarg}={val}")

        kwargs = ', '.join(kwargs)
        if kwargs != '':
            if args != '':
                kwargs = ', ' + kwargs

        return f"{self.class_name}({args}{kwargs})"

    def add_kwarg(self, key, value):
        self.kwargs[key] = value


class If(Block):
    """
    This represents an If/ Elif block in python

    Attributes:
        expr: the expression of the if/elif block
        action: the body of the if/elif block
        if_type: if/elif
        indent_level: the indent level of the If/Elif Block
    """

    def __init__(self, expr: Expr, action: List[Expr], if_type: str = 'if', indent_level=0):
        self.expr = expr
        self.action = action
        self.type = if_type
        super().__init__(indent_level)

    def __str__(self):
        actions = ''
        tabs = self.get_indent_level() * '\t'
        for i, action in enumerate(self.action):
            if i == len(self.action) - 1:
                actions = actions + tabs + '\t' + str(action)
            else:
                actions = actions + tabs + '\t' + str(action) + '\n'
        return f"\n{tabs}{self.type} {str(self.expr)}:\n{actions}"


class IfElse(Block):
    """
    This represents an if-else block in python. Elif blocks can also be added to it

    Attributes:
        else_action: body of the else block
        indent_level: indent level of the Block
        elifs: the elif blocks attached to the if-else block
        if_: the 'if' part of the if-else block
    """

    def __init__(self, else_action: List[Expr], indent_level=0, elifs: List[If] = None, if_: If = None):
        if elifs is None:
            elifs = []
        self.if_ = if_
        self.else_action = else_action
        self.elifs = elifs
        super().__init__(indent_level)

    def __str__(self):
        if self.if_ is None:
            raise CodegenError('No If object attached to IfElse object')
        tabs = self.get_indent_level() * '\t'
        if_action = ''
        for expr in self.if_.action:
            if_action = if_action + tabs + '\t' + str(expr) + '\n'
        if not if_action:
            if_action = 'pass'

        else_action = ''
        for expr in self.else_action:
            else_action = tabs + '\t' + str(expr) + '\n'
        if not else_action:
            else_action = 'pass'

        elifs = '\n'

        for elif_ in self.elifs:
            elifs = elifs + str(elif_) + '\n'

        if elifs == '\n':
            elifs = ''

        return f"\n{tabs}if {str(self.if_.expr)}:\n{if_action.rstrip()}{elifs}{tabs}else:\n{else_action}"

    def add_elif(self, elif_: If):
        """
        This adds an elif statement to the If Else block. You can add the elif statement manually during
        initialisation of the IfElse object but you would have to set indent levels correctly yourself but this
        method does that for you.

        Args:
            elif_: the elif statement to add

        """
        if self.if_ is None:
            elif_.type = 'if'
            self.if_ = elif_
        else:
            elif_.type = 'elif'
            elif_.set_indent_level(self.indent_level)
            self.elifs.append(elif_)
