import datetime
from math import floor
import autopep8
import re
from .utils import stringify, triple_stringify
from .jenna_parts import String, Block, Expr, Function, Method, Class, Variable, ClassInstance, If, IfElse, \
    SingleLineComment, MultilineComment
from .errors import CodegenError

__all__ = [
    'Jenna',
    'String',
    'Block',
    'Expr',
    'Function',
    'Method',
    'Class',
    'Variable',
    'ClassInstance',
    'If',
    'IfElse',
    'SingleLineComment',
    'MultilineComment'
]


# this removes new lines at the end of a string. String forms of blocks should not end with a \n
def cut(string: str) -> str:
    return string.rstrip('\n')


class Jenna:
    """
    Jenna is a class that allows for programmatic writing of python code. All functionalities of the Jenna package are accessed through the Jenna class.

    Attributes:
        output_file: an optional python file that the output code will be written to
        override: this should be True if you want to override the content of the output_file(if set)
    """

    def __init__(self, output_file: str = None, override: bool = True):
        # create a new jenna instance
        mode = 'a+'
        if override is True:
            mode = 'w'
        if output_file is None:
            output_file = 'jenna_output_' + str(floor(datetime.datetime.now().timestamp())) + ".py"
            override = True

        is_valid_file_name = re.match("\w+.py$", output_file)

        if is_valid_file_name is None:
            raise Exception('File is not a python file')
        with open(output_file, mode) as f:
            self.output_file = output_file
            if override is True:
                f.write('# This file was generated by Jenna\n')
            self.format_file()

    def import_package(self, mode=1, **kwargs):
        """
        Imports a package in the jenna output file

        Args:
            mode: import style
                1 - import package
                2 - from package import object
                3 - from package import object as alias
                4 - import package as alias
            **kwargs: package, object. keyword arguments

        """
        if mode == 1:
            statement = f"import {kwargs['package']}"
        elif mode == 2:
            statement = f"from {kwargs['package']} import {kwargs['object']}"
        elif mode == 3:
            statement = f"from {kwargs['package']} import {kwargs['object']} as {kwargs['alias']}"
        elif mode == 4:
            statement = f"import {kwargs['package']} as {kwargs['alias']}"
        else:
            raise Exception("Unrecognised import mode")

        with open(self.output_file, 'a+') as f:
            f.write(f"\n{statement}")
            self.format_file()

    def write_class(self, _class: Class):
        """
        This writes a class to the output file
        Args:
            _class: the class to be written

        Returns:

        """
        with open(self.output_file, 'a+') as f:
            f.write(cut(str(_class)))
            self.format_file()

    def write_variable(self, variable: Variable):
        """
        This writes a variable to the output file
        Args:
            variable: the variable to be written

        Returns:

        """
        with open(self.output_file, 'a+') as f:
            f.write(cut(str(variable)))
            self.format_file()

    def write_if_else(self, if_else: IfElse):
        """
        This writes an if-else block to the output file
        Args:
            if_else: the if-else block to be written

        Returns:

        """
        with open(self.output_file, 'a+') as f:
            f.write(cut(str(if_else)))
            self.format_file()

    def write_comment(self, comment: SingleLineComment):
        """
        This writes a single-line comment to the output file

        Args:
            comment: a single line comment object

        """
        with open(self.output_file, 'a+') as f:
            f.write(cut(str(comment)))
            self.format_file()

    def write_multi_line_comment(self, comment: MultilineComment):
        """
        This writes a single-line comment to the output file

        Args:
            comment: a multi-line comment object
        """
        with open(self.output_file, 'a+') as f:
            f.write(cut(str(comment)))
            self.format_file()

    # TODO: HEY
    def write_block(self, block: Block):
        """
        This writes a block object to the output file

        Args:
            block: a Block object
        """
        with open(self.output_file, 'a+') as f:
            f.write(cut(str(block)))
            self.format_file()

    def format_file(self):
        """
        This formats the output file
        """
        autopep8.fix_file(self.output_file)
