def match_clockin_query_expr(expr, user_clockins):

    # if no limits, return True
    if not len(expr):
        return True

    expr += '#' # end symbol

    has = lambda x: x in user_clockins
    is_ldim = lambda x: x in ('(', u'（')
    is_rdim = lambda x: x in (')', u'）')
    is_empty = lambda x: not x.strip() or x == u'了' or x == u'但'
    symbols = {
        u'#': (-3, 0),

        u'(': (3, 0),
        u'（': (3, 0),
        u')': (3, 0),
        u'）': (3, 0),

        u'未': (2, 1, lambda l1: not l1),
        u'且': (1, 2, lambda l1, l2: l1 and l2),
        u'或': (0, 2, lambda l1, l2: l1 or l2),
    }
    is_literal = lambda x: x not in symbols.keys()
    default_symbol = u'且'

    # lexing
    def lex_tokens():
        literal = ''
        for ch in expr:
            # ' '
            if is_empty(ch):
                continue
            # symbols
            if not is_literal(ch):
                if literal:
                    yield has(literal)
                    if symbols[ch][1] == 1:
                        yield default_symbol
                literal = ''
                yield ch
                continue
            # otherwise: literals
            literal += ch
        if literal:
            yield has(literal)
    
    # parsing
    try:
        literal_stack = []
        op_stack = []
        for token in lex_tokens():
            if is_literal(token):
                literal_stack.append(token)
            else:
                while len(op_stack) and not is_ldim(op_stack[-1]) \
                    and (not (symbols[token][1] == 1 and symbols[op_stack[-1]][1] == 1)) \
                    and ((symbols[op_stack[-1]][0] >= symbols[token][0] \
                        or is_rdim(token))):
                    literals = [literal_stack.pop() for i in range(symbols[op_stack[-1]][1])]
                    literal_stack.append(symbols[op_stack[-1]][2](*literals))
                    op_stack.pop()
                
                if is_rdim(token):
                    if len(op_stack) and is_ldim(op_stack[-1]):
                        op_stack.pop()
                else:
                    op_stack.append(token)

        return literal_stack[0]
    except IndexError:
        return False
