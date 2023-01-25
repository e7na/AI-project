import lolviz as lv


def gr_dict_html(
    title, items, highlight=None, bgcolor=lv.YELLOW, separator="&rarr;", reprkey=True
):
    ptrs = []
    atoms = []
    # by3ml check 3la kol el static values
    for it in items:
        if lv.isatom(it[2]):
            atoms.append(it)
        else:
            ptrs.append(it)
        for t in atoms:
            if t[1] == "is_sol":
                bgcolor = "#00FF00"
        header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="1" CELLSPACING="0">\n'
        blankrow = (
            '<tr><td colspan="3" cellpadding="1" border="0" bgcolor="%s"></td></tr>'
            % (bgcolor)
        )
        rows = []
    if len(items) > 0:
        for label, key, value in atoms + ptrs:  # do atoms first then ptrs
            if label == "is_sol":
                continue
            font = "Helvetica"
            if highlight is not None and key in highlight:
                font = "Times-Italic"
            if separator is not None:
                name = (
                    '<td port="%s_label" cellspacing="0" cellpadding="0" bgcolor="%s" border="0" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n'
                    % (label, bgcolor, font, repr(key) if reprkey else key)
                )
                sep = (
                    '<td cellpadding="0" border="0" valign="bottom"><font color="#444443" point-size="9">%s</font></td>'
                    % separator
                )
            else:
                name = (
                    '<td port="%s_label" cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="r" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n'
                    % (label, bgcolor, font, repr(key) if reprkey else key)
                )
                sep = '<td cellspacing="0" cellpadding="0" border="0"></td>'

            if value is not None:
                if len(str(value)) > lv.prefs.max_str_len:
                    value = lv.abbrev_and_escape(str(value))
                v = repr(value)
            else:
                v = "   "
            value = (
                '<td port="%s" cellspacing="0" cellpadding="1" bgcolor="%s" border="0" align="left"><font color="#444443" point-size="11"> %s</font></td>\n'
                % (label, bgcolor, v)
            )
            row = "<tr>" + name + sep + value + "</tr>\n"
            rows.append(row)
    else:
        rows.append(
            '<tr><td cellspacing="0" cellpadding="0" border="0"><font point-size="9"> ... </font></td></tr>\n'
        )

    tail = "</table>\n"
    return header + blankrow.join(rows) + tail


def obj_node(p, varnames=None):
    s = ""
    nodename = "node%d" % id(p)
    if type(p) == lv.types.FrameType:
        frame = p
        info = lv.inspect.getframeinfo(frame)
        caller_scopename = info[2]
        if caller_scopename == "<module>":
            caller_scopename = "globals"
        argnames, _, _ = lv.inspect.getargs(frame.f_code)
        items = []
        # do args first to get proper order
        for arg in argnames:
            if varnames is not None and arg not in varnames:
                continue
            v = frame.f_locals[arg]
            if lv.isatom(v):
                items.append((arg, arg, v))
            else:
                items.append((arg, arg, None))
        for k, v in frame.f_locals.items():
            if varnames is not None and k not in varnames:
                continue
            if k in argnames:
                continue
            if lv.ignoresym((k, v)):
                continue
            if lv.isatom(v):
                items.append((k, k, v))
            else:
                items.append((k, k, None))
        s += "// FRAME %s\n" % caller_scopename
        s += lv.gr_dict_node(
            nodename,
            caller_scopename,
            items,
            highlight=argnames,
            bgcolor=BLUE,
            separator=None,
            reprkey=False,
        )
    elif isinstance(p, dict):
        # print "DRAW DICT", p, '@ node' + nodename
        items = []
        i = 0
        for k, v in p.items():
            if varnames is not None and k not in varnames:
                continue
            if lv.isatom(v):
                items.append((str(i), k, v))
            else:
                items.append((str(i), k, None))
            i += 1
        s += "// DICT\n"
        s += lv.gr_dict_node(nodename, None, items)
    elif isinstance(p, set) and len(p) == 0:  # special case "empty set"
        s += (
            'node%d [margin="0.03", shape=none label=<<font face="Times-Italic" color="#444443" point-size="9">empty set</font>>];\n'
            % id(p)
        )
    elif p is True or p is False:  # Boolean
        s += (
            'node%d [margin="0.03", shape=none label=<<font face="Times-Italic" color="#444443" point-size="9">%s</font>>];\n'
            % (id(p), str(p))
        )
    elif type(p).__module__ == "numpy" and type(p).__name__ == "ndarray":
        s += lv.gr_ndarray_node("node%d" % id(p), p)
    elif type(p).__module__ == "pandas.core.series" and type(p).__name__ == "Series":
        s += lv.gr_ndarray_node("node%d" % id(p), p.values)
    elif type(p).__module__ == "pandas.core.frame" and type(p).__name__ == "DataFrame":
        s += lv.gr_ndarray_node("node%d" % id(p), p.values)
    elif isinstance(p, list) and len(p) == 0:  # special case "empty list"
        s += (
            'node%d [margin="0.03", shape=none label=<<font face="Times-Italic" color="#444443" point-size="9">empty list</font>>];\n'
            % id(p)
        )
    elif hasattr(p, "__iter__") and lv.isatomlist(p) or type(p) == tuple:
        # print "DRAW LIST", p, '@ node' + nodename
        elems = []
        for el in p:
            if lv.isatom(el):
                elems.append(el)
            else:
                elems.append(None)
        if isinstance(p, set):
            s += "// SET of atoms\n"
            s += lv.gr_set_node(nodename, elems)
        else:
            s += "// LIST or ITERATABLE of atoms\n"
            s += lv.gr_list_node(nodename, elems)
    elif hasattr(p, "__iter__"):
        # print "DRAW VERTICAL LIST", p, '@ node' + nodename
        elems = []
        for el in p:
            if lv.isatom(el):
                elems.append(el)
            else:
                elems.append(None)
        s += "// VERTICAL LIST or ITERATABLE\n"
        if isinstance(p, set):
            s += lv.gr_vlol_node(nodename, elems, title="set", showindexes=False)
        else:
            s += lv.gr_vlol_node(nodename, elems)

    elif hasattr(p, "__dict__"):  # generic object
        # print "DRAW OBJ", p, '@ node' + nodename
        items = []
        for k, v in p.__dict__.items():
            if k == "parent":
                continue
            elif lv.isatom(v):
                items.append((k, k, v))
            else:
                items.append((k, k, None))
        s += "// %s OBJECT with fields\n" % p.__class__.__name__
        s += lv.gr_dict_node(
            nodename, p.__class__.__name__, items, separator=None, reprkey=False
        )
    else:
        s += (
            'node%d [margin="0.03", shape=none label=<<font face="Times-Italic" color="#444443" point-size="9">%s</font>>];\n'
            % (id(p), abbrev_and_escape("<%s:%s>" % (type(p).__name__, repr(p))))
        )

    return s


def closure_(p, varnames, visited):
    if p is None or lv.isatom(p):
        return []
    if id(p) in visited:
        return []
    visited.add(id(p))
    result = []
    if type(p) != lv.types.FrameType:
        result.append(p)

    # now chase where we can reach
    if type(p) == lv.types.FrameType:
        frame = p
        info = lv.inspect.getframeinfo(frame)
        for k, v in frame.f_locals.items():
            # error('INCLUDE frame var %s' % k)
            if varnames is not None and k not in varnames:
                continue
            if not lv.ignoresym((k, v)):
                cl = closure_(v, varnames, visited)
                result.extend(cl)
        caller_scopename = info[2]
        if caller_scopename != "<module>":  # stop at globals
            cl = closure_(p.f_back, varnames, visited)
            result.extend(cl)
    elif type(p).__module__ == "numpy" and type(p).__name__ == "ndarray":
        pass  # ndarray added already above; don't chase its elements here
    elif type(p).__module__ == "pandas.core.series" and type(p).__name__ == "Series":
        pass  # pd.Series added already above; don't chase its elements here
    elif type(p).__module__ == "pandas.core.frame" and type(p).__name__ == "DataFrame":
        pass
    elif type(p) == dict:
        for k, q in p.items():
            cl = closure_(q, varnames, visited)
            result.extend(cl)
    elif hasattr(p, "__dict__"):  # regular object like Tree or Node
        for k, q in p.__dict__.items():
            if k != "parent":
                cl = closure_(q, varnames, visited)
                result.extend(cl)
    elif hasattr(p, "__iter__"):  # a list or similar
        for q in p:
            # check if q has a parent attribute
            cl = closure_(q, varnames, visited)
            result.extend(cl)
    return result


def node_edges(p, varnames=None):
    """Return list of (p, fieldname-in-p, q) for all ptrs in p"""
    edges = []
    if type(p) == lv.types.FrameType:
        frame = p
        for k, v in frame.f_locals.items():
            if varnames is not None and k not in varnames:
                continue
            if not lv.ignoresym((k, v)) and not lv.isatom(v) and v is not None:
                edges.append((frame, k, v))
    elif type(p) == dict:
        i = 0
        for k, v in p.items():
            if not lv.isatom(v) and v is not None:
                edges.append((p, str(i), v))
            i += 1
    elif type(p).__module__ == "numpy" and type(p).__name__ == "ndarray":
        pass  # don't chase elements
    elif hasattr(p, "__iter__"):
        for i, el in enumerate(p):
            if not lv.isatom(el) and el is not None:
                edges.append((p, str(i), el))
    elif hasattr(p, "__dict__"):
        for k, v in p.__dict__.items():
            if k == "parent":
                continue
            if not lv.isatom(v) and v is not None:
                edges.append((p, k, v))
    return edges


# overriding the functions inside lolviz
lv.gr_dict_html = gr_dict_html
lv.obj_node = obj_node
lv.node_edges = node_edges
lv.closure_ = closure_
