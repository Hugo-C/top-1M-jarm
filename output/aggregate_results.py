from collections import defaultdict

INVALID_JARM_RESULT = "00000000000000000000000000000000000000000000000000000000000000"


def read_full_csv(path):
    scans = defaultdict(list)
    min_rank = 0
    max_rank = 0
    with open(path) as input:
        # Line example
        # 1,google.com,216.58.214.174,29d3fd00029d29d21c42d43d00041d188e8965256b2536432a9bd447ae607f
        line = input.readline()
        while line != '':
            if not line.strip():
                line = input.readline()
                continue  # skip empty lines
            value = line.strip().split(",")
            rank, domain, ip, jarm_result = value
            rank = int(rank)
            scans[rank].append(value)
            min_rank = min(min_rank, rank)
            max_rank = max(max_rank, rank)
            line = input.readline()
    return scans, min_rank, max_rank


def reduce_full_csv(scans: dict, min_rank, max_rank, output_path):
    with open(output_path, "w") as output:
        for i in range(min_rank, max_rank + 1):
            values = scans[i]
            if values:
                value = get_valid_jarm(values)
                output.write(','.join(value) + '\n')


def get_valid_jarm(values):
    for value in values:
        rank, domain, ip, jarm_result = value
        if jarm_result != INVALID_JARM_RESULT:
            return value
    return values[-1]  # return the last value even if it has an invalid jarm


if __name__ == '__main__':
    scans, min_rank, max_rank = read_full_csv("result_all.csv")
    print(f"Retrieved domain processed ({len(scans)})")
    reduce_full_csv(scans, min_rank, max_rank, "result_aggregated.csv")
