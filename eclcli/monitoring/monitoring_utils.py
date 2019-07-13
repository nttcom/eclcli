# Functions used to do the format work
from six.moves import urllib


def _format_subdict(dict_x, list_it=True):
    if dict_x is None:
        return None

    if len(dict_x) == 0:
        return "[]"

    out = ""
    if not list_it:
        out += "["

    _keys = dict_x.keys()
    for _key in _keys:
        if type(dict_x[_key]) != list and type(dict_x[_key]) != dict:
            out += str(_key)
            out += ": "
            out += str(dict_x[_key])
            if list_it:
                out += ' \n'
            else:
                out += ", "

        if type(dict_x[_key]) == list:
            out += str(_key)
            out += ": "
            out += _format_sublist(dict_x[_key], False)
            if list_it:
                out += ' \n'
            else:
                out += ", "

        if type(dict_x[_key]) == dict:
            out += str(_key)
            out += ": "
            out += _format_subdict(dict_x[_key], False)
            if list_it:
                out += ' \n'
            else:
                out += ", "

    if len(out) > 2:
        out = out[:-2]

    if not list_it:
        out += ']'

    return out


def _format_sublist(list_x, list_it=True):
    if list_x is None:
        return None

    if len(list_x) == 0:
        return "[]"

    if len(list_x) == 1:
        if type(list_x[0]) != list and type(list_x[0]) != dict:
            out = str(list_x[0]) + ', '
            return out
        if type(list_x[0]) == list:
            return _format_sublist(list_x[0], list_it)
        if type(list_x[0]) == dict:
            return _format_subdict(list_x[0], list_it)

    out = ""
    if not list_it:
        out += "["

    for elem in list_x:
        if type(elem) != list and type(elem) != dict:
            out += str(elem)
            if list_it:
                out += ' \n'
            else:
                out += ", "

        if type(elem) == list:
            out += _format_sublist(elem, False)
            if list_it:
                out += ' \n'
            else:
                out += ", "

        if type(elem) == dict:
            out += _format_subdict(elem, False)
            if list_it:
                out += ' \n'
            else:
                out += ", "

    if len(out) > 2:
        out = out[:-2]

    if not list_it:
        out += ']'

    return out


def _format_show_dictionary(dict_x):
    """
    Return a formatted string instead output a dictionary directly
    :param dict_x: a dictionary
    :return: formatted string
    """

    try:
        _keysNames = dict_x.keys()
        pairs = ""

        for _keyName in _keysNames:
            if type(dict_x[_keyName]) != list and type(dict_x[_keyName]) != dict:
                pairs += str(_keyName) + ": " \
                       + str(dict_x[_keyName]) + '\n'
            if type(dict_x[_keyName]) == list:
                pairs += str(_keyName) + ": "
                pairs += _format_sublist(dict_x[_keyName], False) + '\n'
            if type(dict_x[_keyName]) == dict:
                pairs += str(_keyName) + ": "
                pairs += _format_subdict(dict_x[_keyName], False) + '\n'
        return pairs[:-1]

    except Exception:
        return dict_x


def _format_show_dicts_list(list_x):
    """
    1. Format a list which is full of dicts;
    2. Format a dict;

    :param list_x: a list
    :return: formatted string
    """

    try:
        if list_x is None:
            return None

        if type(list_x) == dict:
            return _format_show_dictionary(list_x)

        else:
            inline = True
            out = ""
            if len(list_x) == 0:
                return out

            if len(list_x) == 1:
                if type(list_x[0]) == dict:
                    out += _format_show_dictionary(list_x[0])
                if type(list_x[0]) == list:
                    out += _format_show_dicts_list[list_x[0]]
                if type(list_x[0]) != dict and type(list_x[0]) != list:
                    out += str(list_x[0])
                return out

            for elem in list_x:
                if type(elem) != list and type(elem) != dict:
                    temp = ""
                    temp += str(elem) + ', '
                    inline = False

                if type(elem) == dict:
                    temp = ""
                    if inline is False:
                        temp += '\n'
                    temp += _format_subdict(elem)
                    temp += " \n"
                    inline = True

                if type(elem) == list:
                    temp = ""
                    if inline is False:
                        temp += '\n'
                    temp += _format_sublist(elem)
                    temp += " \n"
                    inline = True

                out += temp

            if len(out) > 3:
                out = out[:-2]

            return out

    except Exception:
        return list_x


def _format_links(link_x):
    """
    Format links part
    """
    try:
        pairs = ""
        for _dict in link_x:
            pairs += _dict['rel'] + '-> ' + _dict['href'] + '\n'
        return pairs[:-1]

    except Exception:
        return link_x


def _format_links_resource(data):
    """
    Format links of resources while meter_link equaling to 1
    Return formatted list of dicts
    """
    try:

        for elem in data:
            elem._info.setdefault(u'meter_links', [])
            _dicts = elem._info[u'links']
            i = 0

            while i < len(_dicts):
                if _dicts[i][u'rel'] != 'self':

                    elem._info[u'meter_links'].append(_dicts[i])
                    _dicts.pop(i)
                    i -= 1
                i += 1
        return data
    except Exception:
        return data


def get_dict_properties(item, fields, formatters=None):
    if formatters is None:
        formatters = {}

    row = []

    for field in fields:
        data = item[field] if field in item else ''
        if field in formatters:
            row.append(formatters[field](data))
        else:
            row.append(data)
    return tuple(row)


def _dictionary2string(dict_x):
    """
    :param dict_x: a dictionary
    :return: string in one line
    """

    _keysNames = dict_x.keys()
    pairs = ""

    for _keyName in _keysNames:
        pairs += str(_keyName) + ": " \
                   + str(dict_x[_keyName]) + ', '
    return pairs


def _tidy_data_info(info):
    """
    format json data
    """
    try:
        _keys = info.keys()
        for _key in _keys:
            if type(info[_key]) == dict:
                info[_key] = _format_show_dictionary(info[_key])
            if type(info[_key]) == list:
                info[_key] = _format_show_dicts_list(info[_key])
        return info

    except Exception:
        return info


def _make_query(parsed_args):
    """
    make query list
    :return: list of dicts
    """

    if parsed_args.field and parsed_args.value:

        fields = parsed_args.field.split(',')
        values = parsed_args.value.split(',')
        try:
            types = parsed_args.type.split(',')
            ops = parsed_args.op.split(',')
        except Exception:
            types = ["string"]
            ops = ["eq"]

        if len(fields) != len(values):
            print("Error: mismatched fields and values")
            return False
        for i in range(len(fields)):
            try:
                if ops[i] == "":
                    ops[i] = "eq"
            except Exception:
                ops.append("eq")

            try:
                if types[i] == "":
                    types[i] = "string"
            except Exception:
                types.append("string")

        q = []
        for i in range(len(fields)):
            q_temp = {"field": fields[i], "op": ops[i], "type": types[i], "value": values[i]}
            q.append(q_temp)

        return q

    else:
        return None


def _qparams2url(qparams):
    """
    parse qparams to make url segment
    :param qparams:
    :return: parsed url segment
    """
    try:
        if len(qparams) == 0:
            return ""
        assert len(qparams) == 4
        num = len(qparams[0][1])

        path = ""
        for i in range(num):
            for j in range(4):
                path += str(qparams[j][0]) + '=' + str(qparams[j][1][i]) + "&"

        path = path[:-1]
        return path

    except Exception:
        return urllib.parse.urlencode(qparams, doseq=True)


def _print_resp_error(body):
    try:
        info = {"message": body["message"],
                "details": body["title"],
                "code": body["code"]}
        error_msg = "---------error message---------\n"
        error_msg += _format_show_dictionary(info) + '\n'
        error_msg += "-------------------------------"
        return error_msg
    except Exception:
        return body
