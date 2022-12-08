import lolviz as lv
# from lolviz import *


def gr_dict_html(title, items, highlight=None, bgcolor=lv.YELLOW, separator="&rarr;", reprkey=True):
    ptrs = []
    atoms = []
    # by3ml check 3la kol el static values
    for it in items:
        if lv.isatom(it[2]):
            atoms.append(it)
        else:
            ptrs.append(it)
        for t in atoms:
            if t[1] == 'is_sol':
                bgcolor = "#00FF00"
        header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="1" CELLSPACING="0">\n'
        blankrow = '<tr><td colspan="3" cellpadding="1" border="0" bgcolor="%s"></td></tr>' % (bgcolor)
        rows = []
    if len(items) > 0:
        for label, key, value in atoms + ptrs:  # do atoms first then ptrs
            if label == 'is_sol':
                continue
            font = "Helvetica"
            if highlight is not None and key in highlight:
                font = "Times-Italic"
            if separator is not None:
                name = '<td port="%s_label" cellspacing="0" cellpadding="0" bgcolor="%s" border="0" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n' % (
                label, bgcolor, font, repr(key) if reprkey else key)
                sep = '<td cellpadding="0" border="0" valign="bottom"><font color="#444443" point-size="9">%s</font></td>' % separator
            else:
                name = '<td port="%s_label" cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="r" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n' % (
                label, bgcolor, font, repr(key) if reprkey else key)
                sep = '<td cellspacing="0" cellpadding="0" border="0"></td>'

            if value is not None:
                if len(str(value)) > lv.prefs.max_str_len:
                    value = lv.abbrev_and_escape(str(value))
                v = repr(value)
            else:
                v = "   "
            value = '<td port="%s" cellspacing="0" cellpadding="1" bgcolor="%s" border="0" align="left"><font color="#444443" point-size="11"> %s</font></td>\n' % (
            label, bgcolor, v)
            row = '<tr>' + name + sep + value + '</tr>\n'
            rows.append(row)
    else:
        rows.append('<tr><td cellspacing="0" cellpadding="0" border="0"><font point-size="9"> ... </font></td></tr>\n')

    tail = "</table>\n"
    return header + blankrow.join(rows) + tail


# overriding the function inside the module
lv.gr_dict_html = gr_dict_html
