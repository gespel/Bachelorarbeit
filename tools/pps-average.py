import sys

sizes = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 48, 64, 128, 256, 512, 1024]

print("[", end='')
for size in sizes:
    with open(f"../measurements/paper/pps/{size}b_{sys.argv[1]}.txt") as f:
        average = 0
        nr_values = 0
        for line in f.readlines():
            if line != '\n':
                average += int(line)
                nr_values += 1
        print(f"({size}, {int(average/nr_values)}), ", end='')
print("]")