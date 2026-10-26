#!/usr/bin/env python3
"""Extend DolphinPS4's initial library scan to recursively discover games on USB storage."""
from pathlib import Path
import re

source = Path("Source/Core/DolphinNoGUI/PS4XMB.cpp")
text = source.read_text()

if "std::vector<std::filesystem::directory_entry> entries;" in text and "for (const auto& entry : entries)" in text:
    print("USB game discovery patch already applied.")
    raise SystemExit(0)

# Match formatting flexibly; source whitespace can vary after applying the upstream patch.
iterator = re.search(r"(?m)^(\s*)std::filesystem::directory_iterator\s+it\(games_dir,\s*error\);\s*$", text)
if not iterator:
    candidates = [line for line in text.splitlines() if "directory_iterator" in line and "games_dir" in line]
    raise SystemExit("Could not locate ScanLibrary iterator anchor. Candidates: " + repr(candidates))

indent = iterator.group(1)
replacement = """{i}// Search the configured folder plus PS4-visible USB mounts, including subfolders.
{i}std::vector<std::filesystem::directory_entry> entries;
{i}std::vector<std::string> roots = {{games_dir}};
{i}for (int i = 0; i < 8; ++i)
{i}  roots.push_back("/mnt/usb" + std::to_string(i));
{i}roots.push_back("/mnt/ext0");
{i}roots.push_back("/mnt/ext1");
{i}std::set<std::string> seen_paths;
{i}for (const std::string& root : roots)
{i}{{
{i}  std::error_code root_error;
{i}  if (!std::filesystem::is_directory(root, root_error))
{i}    continue;
{i}  std::filesystem::recursive_directory_iterator it(
{i}      root, std::filesystem::directory_options::skip_permission_denied, root_error);
{i}  const std::filesystem::recursive_directory_iterator end;
{i}  while (it != end)
{i}  {{
{i}    std::error_code entry_error;
{i}    if (it->is_regular_file(entry_error))
{i}    {{
{i}      const std::string path = it->path().string();
{i}      if (seen_paths.insert(path).second)
{i}        entries.push_back(*it);
{i}    }}
{i}    it.increment(root_error);
{i}    if (root_error)
{i}      root_error.clear();
{i}  }}
{i}}}
{i}std::sort(entries.begin(), entries.end(), [](const auto& a, const auto& b) {{
{i}  return a.path().string() < b.path().string();
{i}}});""".format(i=indent)
text = text[:iterator.start()] + replacement + text[iterator.end():]
loop = re.search(r"(?m)^(\s*)for\s*\(const auto& entry : it\)\s*$", text)
if not loop:
    raise SystemExit("Iterator declaration patched, but the matching loop was not found.")
text = text[:loop.start()] + loop.group(1) + "for (const auto& entry : entries)" + text[loop.end():]
source.write_text(text)
print("Applied recursive internal/USB game discovery using flexible source anchors.")
