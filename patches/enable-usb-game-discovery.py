#!/usr/bin/env python3
"""Extend DolphinPS4's initial library scan to recursively discover games on USB storage.

This is applied to the upstream PS4XMB.cpp after DolphinPS4's own patch. It intentionally
keeps the upstream supported-format checks and metadata parsing, changing only where files
are discovered.
"""
from pathlib import Path

source = Path("Source/Core/DolphinNoGUI/PS4XMB.cpp")
text = source.read_text()
# Patch stable, small anchors rather than depending on the whole iterator block's formatting.
needle = "  std::filesystem::directory_iterator it(games_dir, error);"
if needle in text:
    replacement = """  // Search the configured folder plus PS4-visible USB mounts, including subfolders.
  std::vector<std::filesystem::directory_entry> entries;
  std::vector<std::string> roots = {games_dir};
  for (int i = 0; i < 8; ++i)
    roots.push_back("/mnt/usb" + std::to_string(i));
  roots.push_back("/mnt/ext0");
  roots.push_back("/mnt/ext1");
  std::set<std::string> seen_paths;
  for (const std::string& root : roots)
  {
    std::error_code root_error;
    if (!std::filesystem::is_directory(root, root_error))
      continue;
    std::filesystem::recursive_directory_iterator it(
        root, std::filesystem::directory_options::skip_permission_denied, root_error);
    const std::filesystem::recursive_directory_iterator end;
    while (it != end)
    {
      std::error_code entry_error;
      if (it->is_regular_file(entry_error))
      {
        const std::string path = it->path().string();
        if (seen_paths.insert(path).second)
          entries.push_back(*it);
      }
      it.increment(root_error);
      if (root_error)
        root_error.clear();
    }
  }
  std::sort(entries.begin(), entries.end(), [](const auto& a, const auto& b) {
    return a.path().string() < b.path().string();
  });"""
    text = text.replace(needle, replacement, 1)
    loop = "  for (const auto& entry : it)"
    if loop not in text:
      raise SystemExit("Iterator declaration found, but expected loop anchor is missing.")
    text = text.replace(loop, "  for (const auto& entry : entries)", 1)
    source.write_text(text)
    print("Applied recursive internal/USB game discovery using stable anchors.")
elif "std::vector<std::filesystem::directory_entry> entries;" in text and "for (const auto& entry : entries)" in text:
    print("USB game discovery patch already applied.")
else:
    raise SystemExit("Could not find safe iterator anchor; no source changes made.")
