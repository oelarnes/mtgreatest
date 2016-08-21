def str_reverse(s):
    char_list = [s[-j-1] for j in range(len(s))]
    return ''.join(char_list)

def standardize_name(name):
    #Always only one name after comma
    if ', ' in name:
        name_part = name.partition(', ')
        name = name_part[2] + ' ' + name_part[0]
    first_last = name.split(' ')
    return ' '.join(first_last[1:]) + ', ' + first_last[0]

def indexOf(li, el):
  try:
    return li.index(el)
  except:
    return None
