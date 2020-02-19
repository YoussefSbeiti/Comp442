from Lexer import *


myfile   = open('../../lexpositivegrading.src' , 'rt')
contents = myfile.read()      # read the entire file into a string
myfile.close()

# Build the lexer
lexer = Lexer()
lexer.build()

# Give the lexer some input
lexer.lexer.input(contents)

outFile = open('tokens.txt' , 'w')

print(lexer.tokens)

# Tokenize
while True:
    tok = lexer.lexer.token()
    if not tok: 
        break      # No more input
    outFile.write(tok.type )