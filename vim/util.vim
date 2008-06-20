python << EOF
import vim
import re
def fixspaces():
    cb = vim.current.buffer
    start, bla = vim.current.buffer.mark('<')
    end, bla = vim.current.buffer.mark('>')
    for i in xrange(start, end):
        line = cb[i]
        cb[i] = re.sub('^  (\S)', '    \\1', line)

def commas(spaces=15):
    cb = vim.current.buffer
    start, bla = vim.current.buffer.mark('<')
    end, bla = vim.current.buffer.mark('>')
    for i in xrange(start, end):
        line = cb[i]
        if not line or ',' not in line: continue
        start, end = line.split(',', 1)
        cb[i] = '%s,%s%s' % (start, ' '*(spaces - len(start)), end.lstrip())

