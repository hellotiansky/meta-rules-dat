#!/usr/bin/env python3
import json
import os
import datetime
from pathlib import Path

MAPPING = {
    "domain": "DOMAIN",
    "domain_suffix": "DOMAIN-SUFFIX",
    "domain_keyword": "DOMAIN-KEYWORD",
    "domain_regex": "URL-REGEX",
    "ip_cidr": "IP-CIDR",
}

def json_to_list(json_path: Path):
    """把单个 json 转成同目录下的 .list 文件"""
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"✗ 读取失败 {json_path}: {e}")
        return

    header = (
        f"# NAME: {json_path.stem}\n"
        f"# UPDATED: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    counts = {}
    lines = []

    for rule in data.get("rules", []):
        for key, values in rule.items():
            if key not in MAPPING:
                continue
            prefix = MAPPING[key]
            if isinstance(values, str):
                values = [values]
            counts[prefix] = counts.get(prefix, 0) + len(values)
            for v in values:
                lines.append(f"{prefix},{str(v).lstrip('.')}")

    for k, v in counts.items():
        header += f"# {k}: {v}\n"
    header += f"# TOTAL: {sum(counts.values())}\n"

    list_path = json_path.with_suffix(".list")
    with open(list_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(lines) + "\n")
    print(f"✓ {list_path}")

def txt_to_all(txt_path: Path, singbox_bin: str = "./sing-box"):
    """txt → json → srs → list"""
    domains = []
    with open(txt_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                domains.append(line.lstrip("."))

    if not domains:
        print(f"⚠ 空文件跳过: {txt_path}")
        return

    base = txt_path.with_suffix("")          # 去掉 .txt
    json_path = base.with_suffix(".json")
    srs_path = base.with_suffix(".srs")
    list_path = base.with_suffix(".list")

    # 1. 生成 json
    json_data = {
        "version": 2,
        "rules": [{"domain_suffix": domains}]
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"✓ {json_path}")

    # 2. 生成 srs
    ret = os.system(f"{singbox_bin} rule-set compile -o {srs_path} {json_path}")
    if ret != 0:
        print(f"✗ 编译 srs 失败: {txt_path}")
        return
    print(f"✓ {srs_path}")

    # 3. 生成 list
    json_to_list(json_path)

def main():
    print("===== 开始转换 geo 目录下的 json =====")
    geo_dir = Path("geo")
    if geo_dir.exists():
        for json_file in geo_dir.rglob("*.json"):
            json_to_list(json_file)
    else:
        print("⚠ geo 目录不存在")

    print("\n===== 开始处理 my_custom_rules =====")
    custom_dir = Path("my_custom_rules")
    if custom_dir.exists():
        for txt_file in sorted(custom_dir.glob("*.txt")):
            txt_to_all(txt_file)
    else:
        print("⚠ my_custom_rules 目录不存在")

    print("\n全部完成！")

if __name__ == "__main__":
    main()
