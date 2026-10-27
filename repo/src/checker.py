"""
ClearSite - rule-based accessibility checker (non-AI baseline / Checkpoint 1-2 prototype).

Checks implemented:
  1. Missing or empty alt attributes on <img> tags
  2. Low text/background contrast ratio (WCAG 2.1 AA threshold: 4.5:1 for normal text)
  3. Form inputs with no associated <label>
  4. Non-descriptive link text ("click here", "read more", etc.)
  5. Heading order skips (e.g., h1 -> h3 with no h2)
"""

import json
import re
import sys
from html.parser import HTMLParser


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(hex1, hex2):
    l1 = relative_luminance(hex_to_rgb(hex1))
    l2 = relative_luminance(hex_to_rgb(hex2))
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


NON_DESCRIPTIVE_LINK_TEXT = {"click here", "read more", "here", "more", "link"}


class AccessibilityChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.issues = []
        self.heading_stack = []
        self._current_tag = None
        self._current_text = ""
        self._label_for_ids = set()
        self._input_ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self._current_tag = tag

        if tag == "img":
            alt = attrs.get("alt")
            src = attrs.get("src", "unknown")
            role = attrs.get("role")
            if alt is None:
                self.issues.append({
                    "rule": "img-missing-alt", "severity": "error",
                    "element": f'<img src="{src}">',
                    "message": "Image has no alt attribute at all.",
                })
            elif alt.strip() == "" and role != "presentation":
                self.issues.append({
                    "rule": "img-empty-alt", "severity": "warning",
                    "element": f'<img src="{src}" alt="">',
                    "message": "Image has an empty alt attribute; only acceptable for purely decorative images.",
                })

        if tag == "label":
            for_id = attrs.get("for")
            if for_id:
                self._label_for_ids.add(for_id)

        if tag == "input":
            input_id = attrs.get("id")
            input_type = attrs.get("type", "text")
            if input_type not in ("hidden", "submit", "button"):
                self._input_ids.append((input_id, input_type))

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            if self.heading_stack and level > self.heading_stack[-1] + 1:
                self.issues.append({
                    "rule": "heading-skip", "severity": "warning",
                    "element": f"<{tag}>",
                    "message": f"Heading level jumps from h{self.heading_stack[-1]} to h{level}, skipping a level.",
                })
            self.heading_stack.append(level)

        if tag == "p":
            style = attrs.get("style", "")
            fg = re.search(r"color:\s*(#[0-9a-fA-F]{3,6})", style)
            bg = re.search(r"background-color:\s*(#[0-9a-fA-F]{3,6})", style)
            if fg and bg:
                ratio = contrast_ratio(fg.group(1), bg.group(1))
                if ratio < 4.5:
                    self.issues.append({
                        "rule": "low-contrast-text", "severity": "error",
                        "element": f'<p style="color:{fg.group(1)}; background-color:{bg.group(1)}">',
                        "message": f"Contrast ratio is {ratio:.2f}:1, below the WCAG 2.1 AA minimum of 4.5:1.",
                    })

        if tag == "a":
            self._current_text = ""

    def handle_data(self, data):
        if self._current_tag == "a":
            self._current_text += data

    def handle_endtag(self, tag):
        if tag == "a":
            text = self._current_text.strip().lower()
            if text in NON_DESCRIPTIVE_LINK_TEXT:
                self.issues.append({
                    "rule": "non-descriptive-link", "severity": "warning",
                    "element": f'<a>{self._current_text.strip()}</a>',
                    "message": f'Link text "{self._current_text.strip()}" does not describe the link destination out of context.',
                })
            self._current_text = ""

    def finalize(self):
        for input_id, input_type in self._input_ids:
            if input_id is None or input_id not in self._label_for_ids:
                self.issues.append({
                    "rule": "input-missing-label", "severity": "error",
                    "element": f'<input type="{input_type}" id="{input_id}">',
                    "message": "Form input has no associated <label for=...>.",
                })


def run_check(html_path):
    with open(html_path, "r") as f:
        html = f.read()
    checker = AccessibilityChecker()
    checker.feed(html)
    checker.finalize()
    return checker.issues


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "pilot/pages/sample_page.html"
    issues = run_check(path)
    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    print(f"ClearSite scan: {path}")
    print(f"Total issues found: {len(issues)}  ({len(errors)} errors, {len(warnings)} warnings)\n")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. [{issue['severity'].upper()}] {issue['rule']}")
        print(f"   Element: {issue['element']}")
        print(f"   {issue['message']}\n")
