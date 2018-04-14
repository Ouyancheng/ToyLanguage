"""
This file contains the definition of the token and the lexer
The lexer can break the program text into a token streams, making it easier for the parser to parse the program

keywords: defined in language_basis.py
id: [A-Za-z][A-Za-z0-9]*
num:
    hexadecimal: 0x[0-9A-Fa-f]+ | 0X[0-9A-Fa-f]+
    octal: 0o[0-7]+ | 0O[0-7]+
    binary: 0b[01]+ | 0B[01]+
    decimal: [0-9]+
"""

from curses.ascii import *
from language_basis import *


class Token:
    """
    The token class
    """

    def __init__(self, classification, value):
        # the classification of the token, the classifications are defined in language_basis.py
        self.classification = classification
        # the value of the token, which is the original string of the token
        self.value = value

    def __str__(self):
        return str('({}, "{}")'.format(self.classification, self.value))


class Lexer:
    """
    The lexer class, once a file_streams is loaded, calling the next_token method will returns the next token
    """

    def __init__(self, file_stream):
        self.file = file_stream  # the file you want to get characters from
        self.line = 1  # current line number, beginning with 1, not used currently
        self.pos = 0  # current position of the current line, beginning with 1, not used currently
        self.current_token = None  # the last token of the lexer
        self.current_char = ' '  # the current character in the lexer
        self.next_token()  # get the next token and store it in self.current_token

    def getchar(self) -> 'nothrow':
        """
        Get the next character from the file
        :return: the next character from the file
        """
        self.pos += 1
        c = self.file.read(1)
        if c == '\n':
            self.line += 1
            self.pos = 0
        return c

    def next_token(self) -> 'throws ValueError':
        """
        Get the next token from the file, the token types are defined in language_basis.py
        This function will identify different tokens, including:
            identifiers / keywords,
            binary / octal / decimal / hexadecimal number literals,
            different operators,
            and single characters.
        This function can also skip white spaces and the comments and the unsupported string literals.
        :return: a Token class if there is a token, otherwise None will be returned
        """
        current_string = ''
        # skip if the file reaches to the end
        if self.current_char == '':
            self.current_token = None
            return None

        # skip white spaces, comments and unsupported string literals
        while True:
            # skip white spaces
            if isspace(self.current_char):
                while isspace(self.current_char):
                    self.current_char = self.getchar()
                    if self.current_char == '':
                        self.current_token = None
                        return None
            # skip comments
            elif self.current_char == '#':
                while self.current_char != '\n':
                    self.current_char = self.getchar()
                    if self.current_char == '':
                        self.current_token = None
                        return None
                self.current_char = self.getchar()  # eat \n
            # skip unsupported string literals
            elif self.current_char == '"' or self.current_char == "'":
                self.current_char = self.getchar()  # eat ' or "
                while self.current_char != '"' and self.current_char != "'":
                    self.current_char = self.getchar()
                    if self.current_char == '':
                        self.current_token = None
                        return None
                self.current_char = self.getchar()  # eat the right side of ' or "
            else:
                break

        # if the current character is alphabet, then this means it's a keyword or an identifier
        # id: [A-Za-z][A-Za-z0-9]*
        if isalpha(self.current_char):
            while isalnum(self.current_char):
                current_string += self.current_char
                self.current_char = self.getchar()
            if current_string in reserved_words:
                self.current_token = Token(classification=reserved_words[current_string], value=current_string)
                return self.current_token
            self.current_token = Token(classification=Id, value=current_string)
            return self.current_token
        # binary, octal and hexadecimal
        # binary 0b01
        # octal 0o01234567
        # hexadecimal 0x1234567890ABCDEF
        elif self.current_char == '0':
            self.current_char = self.getchar()  # eat 0
            # 0x... hexadecimal
            if self.current_char == 'x' or self.current_char == 'X':
                self.current_char = self.getchar()
                while self.current_char in hex_set:
                    current_string += self.current_char
                    self.current_char = self.getchar()
                self.current_token = Token(classification=Num, value=int(current_string, 16))
                return self.current_token
            # 0b... binary
            elif self.current_char == 'b' or self.current_char == 'B':
                self.current_char = self.getchar()
                while self.current_char in bin_set:
                    current_string += self.current_char
                    self.current_char = self.getchar()
                self.current_token = Token(classification=Num, value=int(current_string, 2))
                return self.current_token
            # 0o... octal
            elif self.current_char == 'o' or self.current_char == 'O':
                self.current_char = self.getchar()
                while self.current_char in oct_set:
                    current_string += self.current_char
                    self.current_char = self.getchar()
                self.current_token = Token(classification=Num, value=int(current_string, 8))
                return self.current_token
            # otherwise it's decimal
            else:
                current_string += '0'  # no need to add 0 actually
                while isdigit(self.current_char):
                    current_string += self.current_char
                    self.current_char = self.getchar()
                self.current_token = Token(classification=Num, value=int(current_string, 10))
                return self.current_token
        # decimal
        elif isdigit(self.current_char):
            while isdigit(self.current_char):
                current_string += self.current_char
                self.current_char = self.getchar()
            self.current_token = Token(classification=Num, value=int(current_string, 10))
            return self.current_token
        # tackle with the operator, note that this is a little bit different from the commonly used languages
        # the code below is to split the word containing operator characters (e.g. + - * / > = ~ ^ & | %)
        # and then identify the operator according to the operator word.
        # this means that 1+-2 is not allowed because +- will be treated as one operator and it's not defined
        # we should use 1+ -2 instead.
        # this approach makes the lexer much simpler, because we don't need a finite state machine.
        elif self.current_char in operator_character_set:
            while self.current_char in operator_character_set:
                current_string += self.current_char
                self.current_char = self.getchar()
            if current_string in operators:
                self.current_token = Token(classification=operators[current_string], value=current_string)
                return self.current_token
            else:
                raise ValueError('unknown operator: ' + current_string)
        # single character
        else:
            self.current_token = Token(classification=Character, value=self.current_char)
            self.current_char = self.getchar()
            return self.current_token


# testing the lexer
if __name__ == '__main__':
    file = open('test_parser.txt', 'r')
    lex = Lexer(file)
    tok = lex.current_token
    while tok is not None:
        print(tok)
        tok = lex.next_token()
    exit(0)
