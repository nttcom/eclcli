#Functions used to do the format work
import json

def _format_zone_state(state):
    if isinstance(state, dict) and "available" in state:
        return "Available" if state['available'] else "Unavailable"
    else:
        return state

def _format_subdict(dict_x, list_it = True):
    if dict_x == None:
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


def _format_sublist(list_x, list_it = True):
    if list_x == None:
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

    except:
        return dict_x

def _format_dicts_list_generic(input_list):
    return json.dumps(input_list, indent=4, sort_keys=True)

def _format_show_dicts_list(list_x):
    """
    1. Format a list which is full of dicts;
    2. Format a dict;

    :param list_x: a list
    :return: formatted string
    """
    try:
        if list_x == None:
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
                    out +=  _format_show_dictionary(list_x[0])
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
                    if inline == False:
                        temp += '\n'
                    temp += _format_subdict(elem)
                    temp += " \n"
                    inline = True

                if type(elem) == list:
                    temp = ""
                    if inline == False:
                        temp += '\n'
                    temp += _format_sublist(elem)
                    temp += " \n"
                    inline = True

                out += temp

            if len(out) > 3:
                out = out[:-2]

            return out

    except:
        return list_x


def _format_links(link_x):
    """
    Format links part
    :param link_x: list, which has several dicts in it
    :return: formatted string
    """
    try:
        pairs = ""
        for _dict in link_x:
            pairs += _dict['rel'] + '-> ' + _dict['href'] + '\n'
        return pairs[:-1]

    except:
        return link_x

def _format_imageORflavor(image_link):
    """
    Format image-with-link part
    :param image_link: dictionary, image:id + a link
    :return: formatted string
    """

    try:
        pairs = ""
        pairs += "id: " + str(image_link["id"]) + '\n'
        pairs += "links: " + _format_links(image_link["links"])

        return pairs

    except:
        return image_link

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

def _format_raid_arrays(raid_arrays):
    """
    Format Raid Arrays
    :param raid_arrays: Mixture of string, list and dictionary
    :return: formatted string

    [
        {
            u'disk_hardware_ids':
                [
                    u'813b224a-2cfd-4942-9659-515881502b84',
                    u'ce57f4a8-e79f-4e4a-8594-d40783a2dcfe',
                    u'2c7a4642-6beb-40ba-89eb-ea187d1a477e'
                ],
            u'partitions':
                [
                    {u'name': u'gpt', u'partition_label': u'gpt', u'size': 1},
                    {u'name': u'efi', u'partition_label': u'efi', u'size': 512},
                    {u'name': u'boot',  u'partition_label': u'boot', u'size': 512},
                    {u'lvm': False, u'partition_label': u'root', u'size': 532975},
                    {u'lvm': False, u'partition_label': u'swap', u'size':  16000}
                ],
            u'raid_card_hardware_id': u'd27d25d2-0a47-4c0d-bb48-888c7b8545a5',
            u'primary_storage': True
        }
    ]
    this list has only one element;
    in fact, it's a dictionary;
    """

    try:
        if len(raid_arrays) == 1 and type(raid_arrays) == list:
            raid_arrays = raid_arrays[0]
            _keysNames = raid_arrays.keys()
            for _keyName in _keysNames:
                if type(raid_arrays[_keyName]) == list:
                    #print type(raid_arrays[_keyName][0])
                    if type(raid_arrays[_keyName][0]) == str or type(
                            raid_arrays[_keyName][0]) == unicode:
                        tempStr = "["
                        for elem in raid_arrays[_keyName]:
                            tempStr += str(elem) + ', '
                        if len(tempStr) > 5:
                            raid_arrays[_keyName] = tempStr[:-2] + "]"
                        else:
                            raid_arrays[_keyName] = tempStr + "]"

                    if type(raid_arrays[_keyName][0]) == dict:
                        tempStr = "["
                        for elem_dict in raid_arrays[_keyName]:
                            tempStr += _dictionary2string(raid_arrays[_keyName][0])
                        if len(tempStr) > 5:
                            raid_arrays[_keyName] = tempStr[:-2] + "]"
                        else:
                            raid_arrays[_keyName] = tempStr + "]"

            return _format_show_dictionary(raid_arrays)
        else:
            return raid_arrays

    except:
        return raid_arrays

def _format_nic_physical_ports(ports):
    """
    format nic_physical_ports, divide attached_ports with "-\n"
    :param ports: input nic_physical_ports data
    :return: formatted string
    """

    try:
        temp = _format_show_dicts_list(ports)
        segments = temp.split("attached_ports")
        num = len(segments)
        if num == 1:
            return temp
        out = segments[0] + "attached_ports"
        for i in range(1, num):
            out += segments[i]
            if i != num-1:
                out += "-\n"
                out += "attached_ports"
        return out

    except:
        return ports

def _tidy_data_info(info):
    try:
        _keys = info.keys()
        for _key in _keys:
            if type(info[_key]) == dict:
                info[_key] = _format_show_dictionary(info[_key])
        return info

    except:
        return info
