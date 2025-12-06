#!/usr/bin/env python3
"""patch_jmx.py

Robust JMX patcher for CI usage.

Features:
- Validate inputs and files exist.
- Set ThreadGroup counts safely using XPath search by property name.
- Insert a CSV Data Set Config if not present.
- Optional rules JSON (not required) can describe simple extractors/assertions to insert.

Usage:
  python scripts/patch_jmx.py --input tests/jmeter/baseline.jmx --output tests/jmeter/modified.jmx --users 10 --csv tests/jmeter/data/params.csv

"""
from __future__ import annotations
import argparse
import json
import os
import sys
from lxml import etree


def file_exists(path: str) -> bool:
    return os.path.isfile(path)


def ensure_csv(root: etree._ElementTree, csv_path: str, var_names: str = "username,password") -> None:
    # If CSV Data Set Config already references this file, skip
    xpath = f"//CSVDataSet[stringProp[@name='file' and text()='{csv_path}']]"
    existing = root.xpath(xpath)
    if existing:
        print(f"CSVDataSet for '{csv_path}' already present, skipping insert")
        return
    # Insert CSVDataSet under the top-level test plan hashTree (first hashTree)
    hash_trees = root.findall('.//hashTree')
    if not hash_trees:
        print("No hashTree found in JMX; cannot insert CSV Data Set Config", file=sys.stderr)
        return
    target = hash_trees[0]
    csv_xml = (
        f"<CSVDataSet guiclass='TestBeanGUI' testclass='CSVDataSet' testname='CSV Data Set Config'>"
        f"<stringProp name='delimiter'>,</stringProp>"
        f"<stringProp name='file'>{csv_path}</stringProp>"
        f"<stringProp name='variableNames'>{var_names}</stringProp>"
        f"<boolProp name='quotedData'>false</boolProp>"
        f"<boolProp name='recycle'>true</boolProp>"
        f"<boolProp name='stopThread'>false</boolProp>"
        f"<stringProp name='shareMode'>shareMode.all</stringProp>"
        f"</CSVDataSet>"
    )
    elem = etree.fromstring(csv_xml)
    target.insert(0, elem)
    print(f"Inserted CSVDataSet pointing to {csv_path}")


def set_thread_counts(root: etree._ElementTree, users: int) -> None:
    nodes = root.xpath("//stringProp[@name='ThreadGroup.num_threads']")
    if not nodes:
        print("No ThreadGroup.num_threads nodes found; ensure ThreadGroup exists", file=sys.stderr)
        return
    for n in nodes:
        n.text = str(users)
    print(f"Set {len(nodes)} ThreadGroup.num_threads to {users}")


def apply_rules(root: etree._ElementTree, rules_path: str) -> None:
    if not rules_path or not file_exists(rules_path):
        return
    try:
        with open(rules_path, 'r', encoding='utf-8') as fh:
            rules = json.load(fh)
    except Exception as e:
        print(f"Failed to load rules JSON: {e}", file=sys.stderr)
        return
    # Example rule format (simple): {"add_regex": [{"sampler_name": "Login", "refname": "auth_token", "regex": "token\\\":\\\"(.+?)\\\""}]}
    for r in rules.get('add_regex', []):
        sampler_name = r.get('sampler_name')
        refname = r.get('refname', 'extracted')
        regex = r.get('regex')
        if not sampler_name or not regex:
            continue
        # Find sampler by testname attribute
        samplers = root.xpath(f"//HTTPSamplerProxy[@testname='{sampler_name}']")
        if not samplers:
            print(f"Sampler '{sampler_name}' not found for regex insertion", file=sys.stderr)
            continue
        sampler = samplers[0]
        parent = sampler.getparent()
        regex_xml = (
            f"<RegexExtractor guiclass='RegexExtractorGui' testclass='RegexExtractor' testname='{refname}'>"
            f"<stringProp name='RegexExtractor.useHeaders'>false</stringProp>"
            f"<stringProp name='RegexExtractor.refname'>{refname}</stringProp>"
            f"<stringProp name='RegexExtractor.regex'>{regex}</stringProp>"
            f"<stringProp name='RegexExtractor.template'>$1$</stringProp>"
            f"<stringProp name='RegexExtractor.default'>NOT_FOUND</stringProp>"
            f"</RegexExtractor>"
        )
        try:
            elem = etree.fromstring(regex_xml)
            parent.append(elem)
            print(f"Inserted RegexExtractor '{refname}' under sampler '{sampler_name}'")
        except Exception as e:
            print(f"Failed to insert RegexExtractor: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--users', type=int, default=1)
    parser.add_argument('--csv', help='CSV file to insert')
    parser.add_argument('--rules', help='Optional JSON file with rules to apply')
    args = parser.parse_args()

    if not file_exists(args.input):
        print(f"Input JMX not found: {args.input}", file=sys.stderr)
        sys.exit(2)
    if args.csv and not file_exists(args.csv):
        print(f"CSV file specified but not found: {args.csv}", file=sys.stderr)
        sys.exit(2)

    parser_xml = etree.XMLParser(remove_blank_text=True)
    try:
        tree = etree.parse(args.input, parser_xml)
    except Exception as e:
        print(f"Failed to parse JMX: {e}", file=sys.stderr)
        sys.exit(3)
    root = tree.getroot()

    set_thread_counts(root, args.users)
    if args.csv:
        ensure_csv(root, args.csv)
    if args.rules:
        apply_rules(root, args.rules)

    try:
        tree.write(args.output, pretty_print=True, xml_declaration=True, encoding='utf-8')
        print(f'Wrote modified JMX to {args.output}')
    except Exception as e:
        print(f"Failed to write output JMX: {e}", file=sys.stderr)
        sys.exit(4)


if __name__ == '__main__':
    main()
