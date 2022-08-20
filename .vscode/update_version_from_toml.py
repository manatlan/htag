import re,tomlkit

file='htag/__init__.py'
content = open(file,'r+').read()
v=tomlkit.parse(open('pyproject.toml').read())['tool']['poetry']['version']
with open(file,'w+') as fid:
    fid.write( re.sub(r'__version__ = [^#]*',f'__version__ = \'{v}\' ',content,1) )
assert v in open(file,'r+').read()
print(f'File [{file}] modified => htag.__version__ updated to [{v}] !')