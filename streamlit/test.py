from inspect import getsourcefile
from os.path import abspath

print(abspath(getsourcefile(lambda:0)))