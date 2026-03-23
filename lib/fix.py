import json
import os
import time


def _is_key_start(ch):
    return ch.isalpha() or ch.isdigit() or ch in "_-"


def _is_key_char(ch):
    return ch.isalnum() or ch in "_-"


def quote_unquoted_keys(content):
    """Quote unquoted object keys without touching string literals."""
    out = []
    stack = []
    i = 0
    n = len(content)
    in_string = False
    escape = False

    while i < n:
        ch = content[i]

        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == '{':
            stack.append({"type": "object", "expect_key": True})
            out.append(ch)
            i += 1
            continue

        if ch == '[':
            stack.append({"type": "array"})
            out.append(ch)
            i += 1
            continue

        if ch == '}':
            if stack:
                stack.pop()
            out.append(ch)
            i += 1
            continue

        if ch == ']':
            if stack:
                stack.pop()
            out.append(ch)
            i += 1
            continue

        if ch == ',':
            if stack and stack[-1].get("type") == "object":
                stack[-1]["expect_key"] = True
            out.append(ch)
            i += 1
            continue

        if ch == ':':
            if stack and stack[-1].get("type") == "object":
                stack[-1]["expect_key"] = False
            out.append(ch)
            i += 1
            continue

        if (
            stack
            and stack[-1].get("type") == "object"
            and stack[-1].get("expect_key")
            and _is_key_start(ch)
        ):
            j = i
            while j < n and _is_key_char(content[j]):
                j += 1

            k = j
            while k < n and content[k].isspace():
                k += 1

            if k < n and content[k] == ':':
                key = content[i:j]
                out.append('"')
                out.append(key)
                out.append('"')
                i = j
                continue

        out.append(ch)
        i += 1

    return "".join(out)


def remove_trailing_commas(content):
    """Remove trailing commas before ] or } in non-string context."""
    out = []
    i = 0
    n = len(content)
    in_string = False
    escape = False

    while i < n:
        ch = content[i]

        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == ',':
            j = i + 1
            while j < n and content[j].isspace():
                j += 1
            if j < n and content[j] in '}]':
                i += 1
                continue

        out.append(ch)
        i += 1

    return "".join(out)


def normalize_loose_json(content):
    content = quote_unquoted_keys(content)
    content = remove_trailing_commas(content)
    return content


def robust_fix_and_sort(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"错误: 找不到文件 {input_path}")
        return

    print(f"开始处理: {input_path}")
    start_time = time.time()

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    print("正在修复非标准格式 (处理键名和末尾逗号)...")

    try:
        # Fast path: already valid JSON
        data = json.loads(content)
    except json.JSONDecodeError:
        fixed_content = normalize_loose_json(content)
        try:
            data = json.loads(fixed_content)
        except json.JSONDecodeError as e:
            print("\n❌ 解析失败！")
            start = max(0, e.pos - 80)
            end = min(len(fixed_content), e.pos + 80)
            print(f"错误附近文本: ...{fixed_content[start:end]}...")
            return

    try:
        print("正在保存格式化后的 JSON (带缩进和排序)...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)

        end_time = time.time()
        print("\n✨ 转换成功！")
        print(f"⏱️ 耗时: {end_time - start_time:.2f} 秒")
        print(f"📂 已保存至: {output_path}")
    except Exception as e:
        print(f"发生意外错误: {e}")


if __name__ == "__main__":
    robust_fix_and_sort('particle_emitters_flex.json', 'particle_emitters_fixed.json')
