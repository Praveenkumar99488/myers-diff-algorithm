import sys
from array import array


def read_file(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None

    lines = data.split(b"\n")

    if len(lines) > 0 and lines[-1] == b"":
        lines.pop()

    return lines


def myers_diff(a, b):
    n = len(a)
    m = len(b)

    max_d = n + m
    offset = max_d

    v = [0] * (2 * max_d + 1)
    trace = []

    v[offset + 1] = 0

    for d in range(max_d + 1):

        # Save V before processing this D.
        trace.append(v.copy())

        for k in range(-d, d + 1, 2):

            index = offset + k

            if k == -d:
                x = v[index + 1]

            elif k == d:
                x = v[index - 1] + 1

            else:
                down = v[index + 1]
                right = v[index - 1] + 1

                if down > right:
                    x = down
                else:
                    x = right

            y = x - k

            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[index] = x

            if x >= n and y >= m:
                return backtrack(a, b, trace, d, k, offset)

    return []


def backtrack(a, b, trace, d, k, offset):
    operations = []

    x = len(a)
    y = len(b)

    for current_d in range(d, 0, -1):

        v = trace[current_d]

        if k == -current_d:
            previous_k = k + 1

        elif k == current_d:
            previous_k = k - 1

        else:
            down = v[offset + k + 1]
            right = v[offset + k - 1] + 1

            if down > right:
                previous_k = k + 1
            else:
                previous_k = k - 1

        previous_x = v[offset + previous_k]
        previous_y = previous_x - previous_k

        # Follow the diagonal: unchanged characters.
        while x > previous_x and y > previous_y:
            operations.append(("keep", a[x - 1]))
            x -= 1
            y -= 1

        # One edit operation.
        if x == previous_x:
            operations.append(("insert", b[y - 1]))
            y -= 1
        else:
            operations.append(("delete", a[x - 1]))
            x -= 1

        k = previous_k

    # Remaining diagonal at the beginning.
    while x > 0 and y > 0:
        operations.append(("keep", a[x - 1]))
        x -= 1
        y -= 1

    operations.reverse()

    return operations


def print_lines_diff(operations):
    i = 0

    while i < len(operations):

        if operations[i][0] == "keep":
            line = operations[i][1]
            sys.stdout.buffer.write(b" " + line + b"\n")
            i += 1
            continue

        deleted = []
        inserted = []

        while i < len(operations) and operations[i][0] != "keep":

            operation = operations[i][0]
            line = operations[i][1]

            if operation == "delete":
                deleted.append(line)
            else:
                inserted.append(line)

            i += 1

        for line in deleted:
            sys.stdout.buffer.write(b"-" + line + b"\n")

        for line in inserted:
            sys.stdout.buffer.write(b"+" + line + b"\n")


def get_changed_ranges(old_text, new_text):
    old_chars = list(old_text)
    new_chars = list(new_text)

    operations = myers_diff(old_chars, new_chars)

    old_ranges = []
    new_ranges = []

    old_pos = 0
    new_pos = 0

    old_start = None
    new_start = None

    for operation, char in operations:

        if operation == "keep":

            if old_start is not None:
                old_ranges.append((old_start, old_pos))
                old_start = None

            if new_start is not None:
                new_ranges.append((new_start, new_pos))
                new_start = None

            old_pos += 1
            new_pos += 1

        elif operation == "delete":

            if old_start is None:
                old_start = old_pos

            old_pos += 1

        elif operation == "insert":

            if new_start is None:
                new_start = new_pos

            new_pos += 1

    if old_start is not None:
        old_ranges.append((old_start, old_pos))

    if new_start is not None:
        new_ranges.append((new_start, new_pos))

    return old_ranges, new_ranges


def format_ranges(ranges):
    if not ranges:
        return "."

    result = []

    for start, end in ranges:
        result.append(str(start) + "-" + str(end))

    return ",".join(result)


def print_highlight_diff(operations):
    i = 0

    while i < len(operations):

        if operations[i][0] == "keep":

            line = operations[i][1]

            sys.stdout.buffer.write(b" " + line + b"\n")

            i += 1
            continue

        deleted = []
        inserted = []

        while i < len(operations) and operations[i][0] != "keep":

            operation = operations[i][0]
            line = operations[i][1]

            if operation == "delete":
                deleted.append(line)
            else:
                inserted.append(line)

            i += 1

        # Print deletions first.
        for line in deleted:
            sys.stdout.buffer.write(b"-" + line + b"\n")

        # Pair the deleted and inserted lines.
        pair_count = min(len(deleted), len(inserted))

        for j in range(pair_count):

            old_line = deleted[j]
            new_line = inserted[j]

            # Print the new line.
            sys.stdout.buffer.write(b"+" + new_line + b"\n")

            # Decode lines as UTF-8.
            old_text = old_line.decode("utf-8")
            new_text = new_line.decode("utf-8")

            # Find minimum changed character ranges.
            old_ranges, new_ranges = get_changed_ranges(
                old_text,
                new_text
            )

            old_range_text = format_ranges(old_ranges)
            new_range_text = format_ranges(new_ranges)

            marker = (
                "? "
                + old_range_text
                + " | "
                + new_range_text
                + "\n"
            )

            # IMPORTANT:
            # Write ? using stdout.buffer so it appears
            # immediately after the paired + line.
            sys.stdout.buffer.write(marker.encode("ascii"))

        # Remaining inserted lines are unpaired.
        for j in range(pair_count, len(inserted)):

            line = inserted[j]

            sys.stdout.buffer.write(b"+" + line + b"\n")


def main():

    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):

        print(
            "usage: main.py lines|highlight A_PATH B_PATH",
            file=sys.stderr
        )

        return 2

    command = sys.argv[1]
    a_path = sys.argv[2]
    b_path = sys.argv[3]

    a = read_file(a_path)
    b = read_file(b_path)

    if a is None or b is None:
        return 2

    operations = myers_diff(a, b)

    if command == "lines":
        print_lines_diff(operations)

    else:
        print_highlight_diff(operations)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())