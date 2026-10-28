#!/usr/bin/env python3
"""Make the bundled libcurl feature detection work with the OpenOrbis PS4 toolchain.

The OpenOrbis toolchain reports CMAKE_SYSTEM_NAME=Generic, although the target provides
FreeBSD/POSIX sockets. Curl therefore skips its Unix feature defaults and its cross-probes
cannot size target types with the PS4 linker. Apply narrow PS4-only fixes to the bundled
curl CMake files; keep all unrelated curl features unchanged.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
parent = root / "Externals/curl/CMakeLists.txt"
curl_cmake = root / "Externals/curl/curl/CMakeLists.txt"

if not parent.is_file() or not curl_cmake.is_file():
    raise SystemExit(f"Expected bundled curl CMake files under {root}")

p_text = parent.read_text()
ps4_anchor = "if(PS4)\n  # OpenOrbis netinet/in.h"
ps4_insert = (
    "if(PS4)\n"
    "  # OpenOrbis targets FreeBSD/POSIX but reports CMAKE_SYSTEM_NAME=Generic.\n"
    "  # Scope UNIX to curl and use curl's maintained Unix feature cache.\n"
    "  set(UNIX TRUE)\n"
    '  set(_CURL_PREFILL ON CACHE BOOL "Use Unix feature defaults for PS4 curl" FORCE)\n'
    "  # OpenOrbis netinet/in.h"
)
if "Use Unix feature defaults for PS4 curl" not in p_text:
    if ps4_anchor not in p_text:
        raise SystemExit("Could not locate PS4 curl CMake block; upstream patch layout changed")
    p_text = p_text.replace(ps4_anchor, ps4_insert, 1)
    parent.write_text(p_text)

c_text = curl_cmake.read_text()
size_anchor = (
    'check_type_size("curl_socket_t" SIZEOF_CURL_SOCKET_T)\n'
    'cmake_pop_check_state()  # pop curl system headers\n'
    'cmake_pop_check_state()  # pop -D_FILE_OFFSET_BITS=64'
)
size_insert = size_anchor + (
    "\n\n"
    "if(PS4)\n"
    "  # The PS4 cross-linker cannot link CMake's type-size test executables reliably.\n"
    "  # These ABI sizes are fixed for x86_64 OpenOrbis: curl_off_t is int64_t and\n"
    "  # curl_socket_t is int.\n"
    "  set(SIZEOF_CURL_OFF_T 8)\n"
    '  set(SIZEOF_CURL_OFF_T_CODE "#define SIZEOF_CURL_OFF_T 8")\n'
    "  set(SIZEOF_CURL_SOCKET_T 4)\n"
    '  set(SIZEOF_CURL_SOCKET_T_CODE "#define SIZEOF_CURL_SOCKET_T 4")\n'
    "endif()"
)
if 'set(SIZEOF_CURL_OFF_T_CODE "#define SIZEOF_CURL_OFF_T 8")' not in c_text:
    if size_anchor not in c_text:
        raise SystemExit("Could not locate curl_off_t/curl_socket_t CMake checks; upstream curl layout changed")
    c_text = c_text.replace(size_anchor, size_insert, 1)
    curl_cmake.write_text(c_text)

print("Applied PS4 curl POSIX feature defaults and fixed-width ABI type sizes.")
