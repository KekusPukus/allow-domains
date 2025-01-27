#!/usr/bin/python3.10

import tldextract
import urllib.request
import re
from pathlib import Path
import json
import os
import subprocess

rusDomainsInsideOut='Russia/inside'
rusDomainsInsideSrcSingle='src/Russia-domains-inside-single.lst'
rusDomainsInsideCategories='Categories'
rusDomainsInsideServices='Services'
rusDomainsOutsideSrc='src/Russia-domains-outside.lst'
rusDomainsOutsideOut='Russia/outside'
uaDomainsSrc='src/Ukraine-domains-inside.lst'
uaDomainsOut='Ukraine/inside'

def raw(src, out):
    domains = set()
    files = []

    if isinstance(src, list):
        for dir_path in src:
            path = Path(dir_path)
            if path.is_dir():
                files.extend(path.glob('*'))
            elif path.is_file():
                files.append(path)

    for f in files:
        if f.is_file():
            with open(f) as infile:
                    for line in infile:
                        if tldextract.extract(line).suffix:
                            if re.search(r'[^а-я\-]', tldextract.extract(line).domain):
                                domains.add(tldextract.extract(line.rstrip()).fqdn)
                            if not tldextract.extract(line).domain and tldextract.extract(line).suffix:
                                domains.add("." + tldextract.extract(line.rstrip()).suffix)

    domains = sorted(domains)

    with open(f'{out}-raw.lst', 'w') as file:
        for name in domains:
            file.write(f'{name}\n')

def dnsmasq(src, out, remove={'google.com'}):
    domains = set()
    domains_single = set()
    files = []

    if isinstance(src, list):
        for dir_path in src:
            path = Path(dir_path)
            if path.is_dir():
                files.extend(path.glob('*'))
            elif path.is_file():
                files.append(path)

    for f in files:
        if f.is_file():
            with open(f) as infile:
                    for line in infile:
                        if tldextract.extract(line).suffix:
                            if re.search(r'[^а-я\-]', tldextract.extract(line).domain):
                                domains.add(tldextract.extract(line.rstrip()).fqdn)
                            if not tldextract.extract(line).domain and tldextract.extract(line).suffix:
                                domains.add("." + tldextract.extract(line.rstrip()).suffix)

    domains = domains - remove
    domains = sorted(domains)

    with open(f'{out}-dnsmasq-nfset.lst', 'w') as file:
        for name in domains:
            file.write(f'nftset=/{name}/4#inet#fw4#vpn_domains\n')

    with open(f'{out}-dnsmasq-ipset.lst', 'w') as file:
        for name in domains:
            file.write(f'ipset=/{name}/vpn_domains\n')

def clashx(src, out, remove={'google.com'}):
    domains = set()
    domains_single = set()
    files = []

    if isinstance(src, list):
        for dir_path in src:
            path = Path(dir_path)
            if path.is_dir():
                files.extend(path.glob('*'))
            elif path.is_file():
                files.append(path)

    for f in files:
        with open(f) as infile:
                for line in infile:
                    if tldextract.extract(line).suffix:
                        if re.search(r'[^а-я\-]', tldextract.extract(line).domain):
                            domains.add(tldextract.extract(line.rstrip()).fqdn)
                        if not tldextract.extract(line).domain and tldextract.extract(line).suffix:
                            domains.add("." + tldextract.extract(line.rstrip()).suffix)

    domains = domains - remove
    domains = sorted(domains)

    with open(f'{out}-clashx.lst', 'w') as file:
        for name in domains:
            file.write(f'DOMAIN-SUFFIX,{name}\n')

def kvas(src, out, remove={'google.com'}):
    domains = set()
    domains_single = set()
    files = []

    if isinstance(src, list):
        for dir_path in src:
            path = Path(dir_path)
            if path.is_dir():
                files.extend(path.glob('*'))
            elif path.is_file():
                files.append(path)

    for f in files:
        with open(f) as infile:
                for line in infile:
                    if tldextract.extract(line).suffix:
                        if re.search(r'[^а-я\-]', tldextract.extract(line).domain):
                            domains.add(tldextract.extract(line.rstrip()).fqdn)
                        if not tldextract.extract(line).domain and tldextract.extract(line).suffix:
                            domains.add(tldextract.extract(line.rstrip()).suffix)

    domains = sorted(domains)

    with open(f'{out}-kvas.lst', 'w') as file:
        for name in domains:
            file.write(f'{name}\n')

def mikrotik_fwd(src, out, remove={'google.com'}):
    domains = set()
    domains_single = set()
    files = []

    if isinstance(src, list):
        for dir_path in src:
            path = Path(dir_path)
            if path.is_dir():
                files.extend(path.glob('*'))
            elif path.is_file():
                files.append(path)

    for f in files:
        with open(f) as infile:
                for line in infile:
                    if tldextract.extract(line).suffix:
                        if re.search(r'[^а-я\-]', tldextract.extract(line).domain):
                            domains.add(tldextract.extract(line.rstrip()).fqdn)
                        if not tldextract.extract(line).domain and tldextract.extract(line).suffix:
                            domains.add("." + tldextract.extract(line.rstrip()).suffix)

    domains = domains - remove
    domains = sorted(domains)

    with open(f'{out}-mikrotik-fwd.lst', 'w') as file:
        for name in domains:
            file.write(f'/ip dns static add name={name} type=FWD address-list=allow-domains match-subdomain=yes forward-to=localhost\n')

def domains_from_file(filepath):
    domains = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                domain = line.strip()
                if domain:
                    domains.append(domain)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    return domains

def generate_srs(domains, output_name):
    output_directory = 'JSON'
    compiled_output_directory = 'SRS'

    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(compiled_output_directory, exist_ok=True)

    data = {
        "version": 2,
        "rules": [
            {"domain_suffix": domains}
        ]
    }

    json_file_path = os.path.join(output_directory, f"{output_name}.json")
    srs_file_path = os.path.join(compiled_output_directory, f"{output_name}.srs")

    try:
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"JSON file generated: {json_file_path}")

        subprocess.run(
            ["sing-box", "rule-set", "compile", json_file_path, "-o", srs_file_path], check=True
        )
        print(f"Compiled .srs file: {srs_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Compile error {json_file_path}: {e}")
    except Exception as e:
        print(f"Error while processing {output_name}: {e}")

def generate_srs_for_categories(directories, output_json_directory='JSON', compiled_output_directory='SRS'):
    os.makedirs(output_json_directory, exist_ok=True)
    os.makedirs(compiled_output_directory, exist_ok=True)

    for directory in directories:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            if os.path.isfile(file_path):
                domains = []
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        domain = line.strip()
                        if domain:
                            domains.append(domain)

            data = {
                "version": 2,
                "rules": [
                    {
                        "domain_suffix": domains
                    }
                ]
            }

            output_file_path = os.path.join(output_json_directory, f"{os.path.splitext(filename)[0]}.json")

            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                json.dump(data, output_file, indent=4)

            print(f"JSON file generated: {output_file_path}")

    print("\nCompile JSON files to .srs files...")
    for filename in os.listdir(output_json_directory):
        if filename.endswith('.json'):
            json_file_path = os.path.join(output_json_directory, filename)
            srs_file_path = os.path.join(compiled_output_directory, f"{os.path.splitext(filename)[0]}.srs")
            try:
                subprocess.run(
                    ["sing-box", "rule-set", "compile", json_file_path, "-o", srs_file_path], check=True
                )
                print(f"Compiled .srs file: {srs_file_path}")
            except subprocess.CalledProcessError as e:
                print(f"Compile error {json_file_path}: {e}")

if __name__ == '__main__':
    # Russia inside
    Path("Russia").mkdir(parents=True, exist_ok=True)

    removeDomains = {'google.com', 'googletagmanager.com', 'github.com', 'githubusercontent.com', 'githubcopilot.com', 'microsoft.com', 'cloudflare-dns.com', 'parsec.app' }
    removeDomainsKvas = {'google.com', 'googletagmanager.com', 'github.com', 'githubusercontent.com', 'githubcopilot.com', 'microsoft.com', 'cloudflare-dns.com', 'parsec.app', 't.co' }
    
    inside_lists = [rusDomainsInsideCategories, rusDomainsInsideServices]

    raw(inside_lists, rusDomainsInsideOut)
    dnsmasq(inside_lists, rusDomainsInsideOut, removeDomains)
    clashx(inside_lists, rusDomainsInsideOut, removeDomains)
    kvas(inside_lists, rusDomainsInsideOut, removeDomainsKvas)
    mikrotik_fwd(inside_lists, rusDomainsInsideOut, removeDomains)

    # Russia outside
    outside_lists = [rusDomainsOutsideSrc]

    raw(outside_lists, rusDomainsOutsideOut)
    dnsmasq(outside_lists, rusDomainsOutsideOut)
    clashx(outside_lists, rusDomainsOutsideOut)
    kvas(outside_lists, rusDomainsOutsideOut)
    mikrotik_fwd(outside_lists, rusDomainsOutsideOut)

    # Ukraine
    Path("Ukraine").mkdir(parents=True, exist_ok=True)

    urllib.request.urlretrieve("https://uablacklist.net/domains.txt", "uablacklist-domains.lst")
    urllib.request.urlretrieve("https://raw.githubusercontent.com/zhovner/zaborona_help/master/config/domainsdb.txt", "zaboronahelp-domains.lst")

    ua_lists = ['uablacklist-domains.lst', 'zaboronahelp-domains.lst', uaDomainsSrc]
    
    raw(ua_lists, uaDomainsOut)
    dnsmasq(ua_lists, uaDomainsOut)
    clashx(ua_lists, uaDomainsOut)
    kvas(ua_lists, uaDomainsOut)
    mikrotik_fwd(ua_lists, uaDomainsOut)

    for temp_file in ['uablacklist-domains.lst', 'zaboronahelp-domains.lst']:
        Path(temp_file).unlink()

    # Sing-box ruleset main
    russia_inside = domains_from_file('Russia/inside-raw.lst')
    russia_outside = domains_from_file('Russia/outside-raw.lst')
    ukraine_inside = domains_from_file('Ukraine/inside-raw.lst')
    generate_srs(russia_inside, 'russia-inside')
    generate_srs(russia_outside, 'russia-outside')
    generate_srs(ukraine_inside, 'ukraine-inside')

    # Sing-box categories
    directories = ['Categories', 'Services']
    generate_srs_for_categories(directories)
