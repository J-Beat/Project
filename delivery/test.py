from inspect import getsourcefile
from os.path import abspath


print('/'.join(abspath(getsourcefile(lambda:0)).split('/')[:-1]))
