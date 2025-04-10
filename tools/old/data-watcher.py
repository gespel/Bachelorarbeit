import time

while True:
    with open("rtt.txt", "r") as f:
        all_lines = f.readlines()
        last_two = all_lines[-2:]

        l1 = last_two[0].split("-")
        l2 = last_two[1].split("-")

        type_1 = l1[0]
        time_1 = l1[1]

        type_2 = l2[0]
        time_2 = l2[1]

        if type_1 == "s" and type_2 == "r":
            print(f"RTT: {(float(time_2) - float(time_1)) * 1000} ms")
    time.sleep(1)

