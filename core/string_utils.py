import re


def multi_replace(input_string, replace_dict):
    '''
    https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string

    :param input_string:
    :param replace_dict:
    :return:
    '''

    rep = replace_dict

    rep = dict((re.escape(k), v) for k, v in rep.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], input_string)
