class Dum(object):
    pass

def objectify(dictionary):
    obj = Dum()
    [setattr(obj, k, v) for k, v in dictionary.items()]
    return obj
