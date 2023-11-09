
def get_dial_values():
    dials = {}
    with open('./dials/dials.txt', 'r') as file:
        contents = file.read().split(',')
        dials['a'] = contents[0]
        dials['b'] = contents[1]
        dials['c'] = contents[2]
    return (dials['a'], dials['b'], dials['c'])