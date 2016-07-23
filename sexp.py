from string import whitespace

atom_end = set('()"\'') | set(whitespace)

def save(sexp):
    #print 'saving', sexp
    def _save(sexp, level):
        out = '{}('.format(' '*level)
        for i in sexp:
            if type(i) == list:
                #print
                out += '\n'
                out += _save(i, level+1)
                continue
            #print i[0],
            try:
                out += '{} '.format(i[0])
            except TypeError as e:
                out += '{} '.format(i)
        #print ')', #'{})'.format(' '*level)
        out += ')'
        return out
    return _save(sexp, 0)

def parse(sexp):
    # https://gist.github.com/pib/240957/revisions
    stack, i, length = [[]], 0, len(sexp)
    while i < length:
        c = sexp[i]

#        print c, stack
        reading = type(stack[-1])
        if reading == list:
            if   c == '(': stack.append([])
            elif c == ')': 
                stack[-2].append(stack.pop())
                if stack[-1][0] == ('quote',): stack[-2].append(stack.pop())
            elif c == '"': stack.append('')
            elif c == "'": stack.append([('quote',)])
            elif c in whitespace: pass
            else: stack.append((c,))
        elif reading == str:
            if   c == '"': 
                stack[-2].append(stack.pop())
                if stack[-1][0] == ('quote',): stack[-2].append(stack.pop())
            elif c == '\\': 
                i += 1
                stack[-1] += sexp[i]
            else: stack[-1] += c
        elif reading == tuple:
            if c in atom_end:
                atom = stack.pop()
#                if atom[0][0].isdigit():
#                    try:
#                        stack[-1].append((eval(atom[0]),)) #eval(atom[0]))
#                    except:
#                        stack[-1].append(atom) #eval(atom[0]))
#                else: stack[-1].append(atom)
                stack[-1].append(atom)
                if stack[-1][0] == ('quote',): stack[-2].append(stack.pop())
                continue
            else: stack[-1] = ((stack[-1][0] + c),)
        i += 1
    return stack.pop()
