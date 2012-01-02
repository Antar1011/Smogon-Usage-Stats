from operator import itemgetter

def alt_table(): # Ignore; enables the base_speed() function.
    alts = {"Deoxys": {"Normal": "-N", "Attack": "-A", "Defense": "-D", "Speed": "-S"},
            "Wormadam": {"Plant": "", "Sandy": "-G", "Trash": "-S"},
            "Rotom": {"Normal": "", "Heat": "-H", "Wash": "-W", "Frost": "-F", "Fan": "-S", "Mow": "-C"},
            "Giratina": {"Altered": "", "Origin": "-O"},
            "Shaymin": {"Land": "", "Sky": "-S"},
            "Darmanitan": {"Standard": "", "Zen": "-Z"}}
    return alts

def speed_list(): # Ignore; enables the base_speed() function and requires 'statlist.txt' to run.
    speed_dict = {}
    alt_inits = alt_table()
    liner = open("statlist.txt")
    for line in liner:
        line_data = line.split("\t")
        line_stuff = line_data[2].strip().split("(")
        line_name = line_stuff[0].strip()
        if alt_inits.has_key(line_name):
            for forme in alt_inits[line_name]:
                forme_name = line_stuff[1].split()[0]
                if forme == forme_name:
                    line_name += alt_inits[line_name][forme]
        speed_dict[line_name] = int(line_data[8].strip())
    return speed_dict

def stat_list(stats):
    data = open(stats)
    output = {}

    for line in data:
        line = line.split("|")
        piece = [line[2].strip(), int(line[1].strip()), float(line[4].strip()[:-1])]
        output[piece[0]] = [piece[1], piece[2]]

    return output

def changes(old_file, new_file):
    old_data = stat_list(old_file)
    new_data = stat_list(new_file)
    change_list = []

    new_list = new_data.keys()
    old_list = old_data.keys()

    for i in new_list:
        if new_data[i][0] < 101: # Determines number of pokes in final list
            if i in old_list:
                for k in old_list:
                    if i == k:
                        change = [new_data[i][0], i, old_data[k][0] - new_data[i][0]]
                        change_list.append(change)
    change_list.sort()

    return change_list

def tiering(month_1, month_2, month_3):
    m_1 = stat_list(month_1)
    m_2 = stat_list(month_2)
    m_3 = stat_list(month_3)
    l_3 = m_3.keys()
    tier = []

    for poke in l_3:
        val_1 = m_1.get(poke, [0, 0])[1]
        val_2 = m_2.get(poke, [0, 0])[1] * 3
        val_3 = m_3.get(poke, [0, 0])[1] * 20
        rating = (val_1 + val_2 + val_3) / 24.0
        if rating >= 2: # Determines minimum usage percent of each poke in in final list
            datum = [m_3[poke][0], poke, rating]
            tier.append(datum)

    tier = sorted(tier, key=itemgetter(2), reverse=True)
    for x in range(len(tier)):
        tier[x][0] = x + 1

    return tier

def base_speed(input):
    base_list = speed_list()
    bases = []

    for line in range(len(input)):
        # Change banned pokes for different tiers; can add "and input[line][2] >= 3.41" to restrict to only pokes in the tier.
        if input[line][1] != 'Deoxys-S':
            input[line][2] = base_list[input[line][1]]
            bases.append(input[line])
    bases = sorted(bases, key = itemgetter(1))
    bases = sorted(bases, key = itemgetter(2), reverse=True)
    for line in range(len(bases)):
        bases[line][0] = line + 1

    return bases

def draw_graph(input, variable):
    header = " + ---- + --------------- + " + "-" * len(variable) + " + \n"
    title  = " | Rank | Pokemon         | " + variable + " | \n"
    output = header + title + header

    for index in range(len(input)):
        rank = str(input[index][0])
        poke = input[index][1]
        var = input[index][2]
        if variable == "Change":
            var = str(var).rjust(4) + "  "
        elif variable == "Percent":
            var = "%.3f" % var
            var += "%"
            var = var.rjust(7)
        elif variable == "Speed":
            var = str(var).rjust(4) + " "
        # You can add different behaviours for different variables in the same manner here.
        output += " | " + str(rank).rjust(4) + " | " + poke.ljust(16) + "| " + var + " | \n"

    output += header
    return output

tier = "OU" # Can be changed to "UU", "OU1337", etc.
use_file = tier + "Usage.txt"
m1 = "Oct" + use_file
m2 = "Nov" + use_file
m3 = "Dec" + use_file

change = changes(m2, m3)
print draw_graph(change, "Change")

percent = tiering(m1, m2, m3)
print draw_graph(percent, "Percent")

speed = base_speed(percent)
print draw_graph(speed, "Speed")