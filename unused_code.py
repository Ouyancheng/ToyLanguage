# skip white spaces
# while isspace(self.current_char) or self.current_char == '\n':
#     self.current_char = self.getchar()
#     if self.current_char == '':
#         self.current_token = None
#         return None

# # skip preprocessor commands
# if self.current_char == '#':
#     while self.current_char != '\n' and self.current_char != '':
#         self.current_char = self.getchar()
#     self.current_char = self.getchar()
# # strings are not supported
# if self.current_char == "'" or self.current_char == '"':
#     self.current_char = self.getchar()
#     while self.current_char != '"' and self.current_char != "'" and self.current_char != '':
#         self.current_char = self.getchar()
#     self.current_char = self.getchar()
#
# if self.current_char == '':
#     self.current_token = None
#     return None
#
# while isspace(self.current_char) or self.current_char == '\n':
#     self.current_char = self.getchar()
#     if self.current_char == '':
#         self.current_token = None
#         return None
#
# if self.current_char == '':
#     self.current_token = None
#     return None

