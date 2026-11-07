"""What `zpool iostat` prints for the two calls the agent plugin makes.

The agent runs `zpool iostat -ylpq 1 1` for the two header lines and
`zpool iostat -Hylpq <sampling_duration> 1` for the data. The header layout
below follows print_iostat_header_impl() and print_iostat_labels() in
cmd/zpool/zpool_main.c of OpenZFS (checked against master of 2026-11-06):

* the name column is as wide as the longest pool name, at least 10;
* with -p the columns are 15 (capacity, operations, bandwidth), 10 (latency,
  -l) and 6 (queues, -q) wide, without -p all are 5 wide;
* every column is preceded by two spaces; a bottom label is right-aligned
  in its column, a top label starts at (width / columns - len / columns)
  of the columns it spans.

Scripted mode (-H) prints no header and separates the fields by one tab.
With -p a latency of 0 (no I/O of that kind) prints as "-", every other
value as an integer: bytes, operations per second, nanoseconds.

OpenZFS 0.8 has no rebuild columns; they came with sequential resilver in
2.0. ZFS_08 builds that older layout.
"""

ZFS_2 = {
    "default": [("capacity", ["alloc", "free"]),
                ("operations", ["read", "write"]),
                ("bandwidth", ["read", "write"])],
    "latency": [("total_wait", ["read", "write"]),
                ("disk_wait", ["read", "write"]),
                ("syncq_wait", ["read", "write"]),
                ("asyncq_wait", ["read", "write"]),
                ("scrub", ["wait"]),
                ("trim", ["wait"]),
                ("rebuild", ["wait"])],
    "queues": [("syncq_read", ["pend", "activ"]),
               ("syncq_write", ["pend", "activ"]),
               ("asyncq_read", ["pend", "activ"]),
               ("asyncq_write", ["pend", "activ"]),
               ("scrubq_read", ["pend", "activ"]),
               ("trimq_write", ["pend", "activ"]),
               ("rebuildq_write", ["pend", "activ"])],
}

ZFS_08 = {
    "default": ZFS_2["default"],
    "latency": [g for g in ZFS_2["latency"] if g[0] != "rebuild"],
    "queues": [g for g in ZFS_2["queues"] if g[0] != "rebuildq_write"],
}

LITERAL_WIDTH = {"default": 15, "latency": 10, "queues": 6}


def _labels(layout, literal, top):
    out = ""
    for kind in ("default", "latency", "queues"):
        width = LITERAL_WIDTH[kind] if literal else 5
        for title, subs in layout[kind]:
            items = [(title, len(subs))] if top else [(s, 1) for s in subs]
            for name, columns in items:
                span = width * columns + 2 * (columns - 1)
                start = max(0, span // columns - len(name) // columns)
                out += "  " + " " * start + name + " " * max(0, span - start - len(name))
    return out


def header(pools, layout=ZFS_2, literal=True):
    """The first three lines of `zpool iostat -ylpq 1 1`."""
    namewidth = max([10] + [len(p) for p in pools])
    dashes = "-" * namewidth
    for kind in ("default", "latency", "queues"):
        width = LITERAL_WIDTH[kind] if literal else 5
        for _title, subs in layout[kind]:
            dashes += ("  " + "-" * width) * len(subs)
    return [
        " " * namewidth + _labels(layout, literal, top=True),
        "pool".ljust(namewidth) + _labels(layout, literal, top=False),
        dashes,
    ]


def columns(layout=ZFS_2):
    return sum(len(subs) for kind in layout.values() for _t, subs in kind)


# One 10 s sample of a busy 2 x 8 TB mirror and an idle boot pool. The
# values are in the column order of ZFS_2: capacity (bytes), operations
# (1/s), bandwidth (B/s), latencies (ns, "-" when idle), queue depths.
TANK = ["3298534883328", "4698694819840",
        "152", "873", "9961472", "52428800",
        "2412345", "8123456", "1830000", "4210000",
        "15234", "9876", "120345", "3456789",
        "-", "-", "-",
        "0", "0", "0", "0", "0", "0", "12", "4", "0", "0", "0", "0", "0", "0"]

RPOOL = ["21474836480", "85899345920",
         "0", "3", "0", "49152",
         "-", "312000", "-", "250000",
         "-", "-", "-", "41000",
         "-", "-", "-",
         "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]


def scripted(rows):
    """`zpool iostat -Hylpq N 1` output: name, then one tab before each value."""
    return "".join(name + "".join("\t" + v for v in values) + "\n" for name, values in rows)


def table(rows, layout=ZFS_2):
    """`zpool iostat -ylpq 1 1` output: the header and the space-aligned rows."""
    lines = header([n for n, _ in rows], layout)
    namewidth = len(lines[2].split("  ")[0])
    widths = [LITERAL_WIDTH[kind] for kind in ("default", "latency", "queues")
              for _t, subs in layout[kind] for _s in subs]
    for name, values in rows:
        lines.append(name.ljust(namewidth) + "".join(f"  {v:>{w}}" for v, w in zip(values, widths)))
    return "\n".join(lines) + "\n"
