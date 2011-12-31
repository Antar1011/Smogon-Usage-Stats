from operator import itemgetter

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
            datum = [m_1[poke][0], poke, rating]
            tier.append(datum)

    tier = sorted(tier, key=itemgetter(2), reverse=True)
    for x in range(len(tier)):
        tier[x][0] = x + 1

    return tier

def draw_graph(input, variable):
    header = "+ ---- + --------------- + " + "-" * len(variable) + " +\n"
    title  = "| Rank | Pokemon         | " + variable + " |\n"
    output = header + title + header

    for index in range(len(input)):
        rank = str(input[index][0])
        poke = input[index][1]
        var = input[index][2]
        if variable == "Change":
            var = str(var).rjust(4) + "  "
        elif variable == "Percent":
            var = "%.2f" % var
            var += "%"
            var = var.rjust(7)
        # You can add different behaviours for different variables in the same manner here.
        output += "| " + str(rank).rjust(4) + " | " + poke.ljust(16) + "| " + var + " |\n"

    output += header
    return output

change = changes("NovOUUsage.txt", "DecOUUsage.txt")
print draw_graph(change, "Change")

percent = tiering("OctOUUsage.txt", "NovOUUsage.txt", "DecOUUsage.txt")
print draw_graph(percent, "Percent")