#!/usr/bin/env python3
"""Remove duplicate PS4 heap diagnostic exports before linking DolphinPS4."""
from pathlib import Path
import os

p = Path(os.environ["GITHUB_WORKSPACE"]) / "dolphinps4/port/ps4_runtime.cpp"
s = p.read_text()
block = """// Diagnostics.
const char* ps4rt_heap_source(void) {
    getHeap();
    return g_heapPool;
}
size_t ps4rt_heap_size(void) {
    getHeap();
    return g_heapSize;
}
"""
if block not in s:
    raise SystemExit("Expected duplicate heap diagnostics block not found in ps4_runtime.cpp; refusing unsafe edit")
p.write_text(s.replace(block, "", 1))
print("Removed duplicate heap diagnostics; runtime archive remains authoritative")
