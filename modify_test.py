#!/bin/python3
import sys
import os

def get_unit(val):
    """
    """
    index = 0
    for letter in val:
        if letter.isdigit():
            index += 1
        else:
            break

    return index, val[index:]

def has_interval(line):
    """
    """
    values = line.split(':')
    if len(values) == 1:
        return False, None, line

    prefix = values[0]
    value = values[1]

    intervals = value.split('...')
    if len(intervals) == 0:
        return False, None, line

    if len(intervals) != 2:
        return False, None, line

    return True, prefix, intervals

def provide_outstr(line):
    """
    """
    val, prefix, intervals = has_interval(line)
    if val is False:
        return line

    val_min = intervals[0].replace(' ', '')
    val_max_tmp = intervals[1]

    index, unit = get_unit(val_max_tmp)
    val_max = val_max_tmp[:index]

    outstr = ""

    outstr += "{} minimum: {}{}\n".format(prefix, val_min, unit)
    outstr += "{} maximum: {}{}".format(prefix, val_max, unit)

    return outstr

def test_all():
    """
    """
    fnames = os.listdir("mpn/tme")
    for fname in fnames:
        fullpath = os.path.join("mpn/tme", fname)
        with open(fullpath, 'r', encoding='utf-8', errors='ignore') as my_file:
            for line in my_file.readlines():
                print(line)
                outstr = provide_outstr(line)
                print(outstr)

def search_all():
    """
    """
    fnames = os.listdir("mpn/tme")
    for fname in fnames:
        fullpath = os.path.join("mpn/tme", fname)
        with open(fullpath, 'r', encoding='utf-8', errors='ignore') as my_file:
            for line in my_file.readlines():
                out, _, _ = has_interval(line)
                if out is True:
                    print(line)

def main(line, test_type):
    if test_type is None:
        outstr = provide_outstr(line)
        print(outstr)
    elif test_type == "testAll":
        test_all()
    elif test_type == "searchAll":
        search_all()

if __name__ == "__main__":
    line, test_type = None, None

    if len(sys.argv) != 2:
        print("invalid usage")

    if sys.argv[1] in ["testAll", "searchAll"]:
        test_type = sys.argv[1]
    else:
        line = sys.argv[1]

    main(line, test_type)
