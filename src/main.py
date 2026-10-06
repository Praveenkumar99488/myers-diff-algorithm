"""
read_file():
This function reads a file and returns all its lines. It opens the
file in binary mode so that the original file data is kept safely.
The file is divided into separate lines using the newline character.
If there is an empty line at the end of the file, it is removed.
If the file cannot be opened, the function returns None.


myers_diff():
This is the main function that compares the two files or lists.
It uses the Myers Diff algorithm to find the smallest number of
changes needed to change the first list into the second list.
It finds which items are the same, which are deleted, and which
are inserted. The V array stores the position reached during the
comparison. The variable d represents the number of changes being
tried, and k represents the diagonal being used. When two items
are the same, the algorithm continues forward. This matching part
is called a snake. The trace stores information that is needed
later to find the exact changes. When the end of both lists is
reached, the backtrack() function is called.


backtrack():
This function finds the actual changes after the Myers Diff
algorithm finishes its main comparison. It starts from the end
of both lists and moves backwards. It checks whether an item
should be kept, inserted, or deleted. The operations are first
stored in reverse order because the function is moving backwards.
At the end, the operations are reversed so that they are in the
correct order. Finally, the function returns all the operations.


print_lines_diff():
This function prints the normal line-by-line difference between
the two files. A space before a line means the line is the same.
A minus sign means the line was deleted from the old file.
A plus sign means the line was added to the new file. It collects
the deleted and inserted lines and then prints them in a simple
diff format.


get_changed_ranges():
This function finds the exact characters that changed inside two
different lines. It converts both lines into lists of characters
and uses the Myers Diff algorithm again. This time, instead of
comparing complete lines, it compares individual characters.
It keeps track of the positions where characters were deleted or
inserted. Finally, it returns the changed character ranges for
both the old line and the new line.


format_ranges():
This function converts the changed character positions into a
simple format that can be printed. For example, a range such as
(2, 5) is converted into "2-5". If there are multiple ranges,
they are joined using commas. If there is no changed range, the
function returns a dot ".".


print_highlight_diff():
This function prints a detailed difference between the two files.
It first prints the deleted and inserted lines. Then it pairs an
old line with a new line and compares their characters. It calls
get_changed_ranges() to find exactly which character positions
were changed. The minus sign shows the old line, the plus sign
shows the new line, and the question mark shows the positions
where the characters changed.


main():
This function controls the complete program. First, it checks
whether the user has entered the correct command and file paths.
Then it reads both files using read_file(). After that, it compares
the files using myers_diff(). If the user selects "lines", it
prints the normal line differences. If the user selects
"highlight", it prints the detailed character-level differences.
It returns 0 when the program finishes successfully and returns
2 when there is an error.


Program Entry:
This part checks whether the Python file is being run directly.
If it is being run directly, it calls the main() function and
starts the program.
"""

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

    if max_d == 0:
        return []

    v = [0] * (2 * max_d + 3)
    v[offset + 1] = 0

    trace = []

    for d in range(max_d + 1):

        # Save only the V values needed for backtracking.
        if d == 0:
            trace.append((1, [v[offset + 1]]))
        else:
            previous_d = d - 1
            trace.append(
                (
                    previous_d,
                    v[
                        offset - previous_d:
                        offset + previous_d + 1
                    ]
                )
            )

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
                return backtrack(a, b, trace, d, k)

    return []


def backtrack(a, b, trace, d, k):
    operations = []

    x = len(a)
    y = len(b)

    for current_d in range(d, 0, -1):

        previous_d, v = trace[current_d]

        def get_value(diagonal):
            return v[diagonal + previous_d]

        if k == -current_d:
            previous_k = k + 1

        elif k == current_d:
            previous_k = k - 1

        else:
            down = get_value(k + 1)
            right = get_value(k - 1) + 1

            if down > right:
                previous_k = k + 1
            else:
                previous_k = k - 1

        previous_x = get_value(previous_k)
        previous_y = previous_x - previous_k

        while x > previous_x and y > previous_y:
            operations.append(("keep", a[x - 1]))
            x -= 1
            y -= 1

        if x == previous_x:
            operations.append(("insert", b[y - 1]))
            y -= 1
        else:
            operations.append(("delete", a[x - 1]))
            x -= 1

        k = previous_k

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