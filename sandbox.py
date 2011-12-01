import cppy

c = cppy.Cpp(open('tests/demo.cpp'))
ass = c[-1].sub[-11]
t = lambda x, e: cppy.match(cppy.tokenize(x), e)
