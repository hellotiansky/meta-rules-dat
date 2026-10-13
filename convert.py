#!/usr/bin/env python3
import json
import os
import datetime
from pathlib import Path
from collections import defaultdict

MAPPING = {
    "domain": "DOMAIN",
    "domain_suffix": "DOMAIN-SUFFIX",
    "domain_keyword": "DOMAIN-KEYWORD",
    "domain_regex": "URL-REGEX",
    "ip_cidr": "IP-CIDR",
}

REPO = "hellotiansky/meta-rules-dat"
BRANCH = "sing"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
BLOB_BASE = f"https://github.com/{REPO}/blob/{BRANCH}"

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

    base = txt_path.with_suffix("")
    json_path = base.with_suffix(".json")
    srs_path = base.with_suffix(".srs")

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


def generate_readme(dir_path: Path, title: str):
    """为指定目录生成带分类链接的 README.md"""
    if not dir_path.exists():
        return

    # 收集所有规则名称（按 stem 去重）
    names = set()
    for f in dir_path.iterdir():
        if f.is_file() and f.suffix in {".json", ".list", ".srs"}:
            names.add(f.stem)

    names = sorted(names, key=str.lower)
    if not names:
        return

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    relative = dir_path.as_posix()  # 例如 geo/geosite

    lines = [
        f"# {title}",
        "",
        f"> 自动生成于 {now}  |  共 **{len(names)}** 个规则",
        "",
        "## 使用说明",
        "",
        "- **list**：Shadowrocket / Surge / Loon 等直接引用",
        "- **json / srs**：sing-box 使用",
        "",
        "点击下方链接即可跳转到对应文件。",
        "",
        "---",
        "",
        "| 规则名称 | list | json | srs |",
        "|----------|------|------|-----|",
    ]

    for name in names:
        # 处理文件名中的特殊字符（如 @）用于 URL
        encoded = name.replace("@", "%40")
        list_link = f"[list]({BLOB_BASE}/{relative}/{encoded}.list)"
        json_link = f"[json]({BLOB_BASE}/{relative}/{encoded}.json)"
        srs_link  = f"[srs]({BLOB_BASE}/{relative}/{encoded}.srs)"
        lines.append(f"| `{name}` | {list_link} | {json_link} | {srs_link} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### 快速复制 Raw 链接示例（Shadowrocket）")
    lines.append("")
    lines.append("```text")
    lines.append(f"RULE-SET,{RAW_BASE}/{relative}/cn.list,DIRECT")
    lines.append("```")
    lines.append("")

    readme_path = dir_path / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✓ 生成说明文档: {readme_path} （共 {len(names)} 个规则）")


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

    print("\n===== 生成说明文档 =====")
    generate_readme(Path("geo/geosite"), "GeoSite 规则列表")
    generate_readme(Path("geo/geoip"), "GeoIP 规则列表")

    print("\n全部完成！")


if __name__ == "__main__":
    main()
