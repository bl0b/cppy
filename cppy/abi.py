import popen2

def pp(text):
    gcc = popen2.Popen4('gcc -E -')
    gcc.tochild.write(text + '\n')
    gcc.tochild.close()
    return gcc.fromchild.read()
