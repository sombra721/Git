
# checks for an empty string:
#   a null string
#   a string with only double-quote(s)
#   a string with whitespaces, and tabs
def is_empty_string(str):
    # null string.
    if not str:
        return True
    # remove double-quotes, and remove leading and trailing whitespaces.
    line = str.replace('"', '').strip()
    if len(line) <= 0:
        return True
    else:
        return False
