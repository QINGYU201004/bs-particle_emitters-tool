import json
import os
import re
from datetime import datetime


def _split_keywords(raw):
    """Split keyword input by comma, keep non-empty tokens."""
    return [item.strip() for item in raw.split(',') if item.strip()]


def _match_token(text, token):
    if token.startswith('re:'):
        pattern = token[3:]
        try:
            return re.search(pattern, text, flags=re.IGNORECASE) is not None
        except re.error:
            return False
    return token.lower() in text.lower()


def _match_all_tokens(text, raw_keywords):
    tokens = _split_keywords(raw_keywords)
    if not tokens:
        return True
    return all(_match_token(text, token) for token in tokens)


def _safe_part(raw):
    raw = raw.strip()
    if not raw:
        return ''
    return re.sub(r'[^a-zA-Z0-9._-]+', '-', raw)[:80].strip('-')


def _build_output_path(input_path, key_keyword, swf_keyword, output_path=None):
    if output_path:
        return output_path

    key_part = _safe_part(key_keyword)
    swf_part = _safe_part(swf_keyword)
    suffix = "_".join(part for part in (key_part, swf_part) if part)
    if not suffix:
        suffix = "all"

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"extracted_{suffix}_{ts}.json"
    return os.path.join(os.path.dirname(os.path.abspath(input_path)), file_name)


def _collect_movieclip_text(effect):
    clips = effect.get("movieclip", [])
    parts = []
    for clip in clips:
        if not isinstance(clip, dict):
            continue
        swf = clip.get("swf", "")
        name = clip.get("name", "")
        if swf:
            parts.append(str(swf))
        if name:
            parts.append(str(name))
    return " ".join(parts)


def extract_effects_advanced(input_path, key_keyword="", swf_keyword="", output_path=None, limit=0):
    """
    双重搜索提取：
    1. key_keyword: 特效名称关键词，支持逗号分隔多个关键词（AND），支持 re:正则
    2. swf_keyword: 在 movieclip.swf + movieclip.name 中搜索，规则同上

    Args:
        input_path: 输入 JSON 文件路径
        key_keyword: 特效名关键词
        swf_keyword: swf/name 关键词
        output_path: 可选输出路径
        limit: 限制输出数量，0 表示不限制

    Returns:
        dict: {"count": int, "output": str | None}
    """
    if not os.path.exists(input_path):
        print(f"❌ 错误: 找不到输入文件 {input_path}")
        return {"count": 0, "output": None}

    print("🔍 正在读取文件并进行过滤...")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            print("❌ 错误: 输入 JSON 顶层不是对象，无法按特效名筛选。")
            return {"count": 0, "output": None}

        extracted_data = {}
        max_items = max(0, int(limit)) if isinstance(limit, int) else 0

        for key, effect in data.items():
            if not isinstance(effect, dict):
                continue

            name_match = _match_all_tokens(str(key), key_keyword)
            clip_text = _collect_movieclip_text(effect)
            swf_match = _match_all_tokens(clip_text, swf_keyword)

            if name_match and swf_match:
                extracted_data[key] = effect
                if max_items and len(extracted_data) >= max_items:
                    break

        if not extracted_data:
            print(f"❓ 未找到符合条件的特效 (Key: '{key_keyword}', SWF/Name: '{swf_keyword}')。")
            return {"count": 0, "output": None}

        final_output = _build_output_path(input_path, key_keyword, swf_keyword, output_path)

        with open(final_output, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=4, ensure_ascii=False, sort_keys=True)

        keys = list(extracted_data.keys())
        preview = ", ".join(keys[:5])

        print("✨ 提取完成！")
        print(f"📊 匹配数量: {len(extracted_data)}")
        print(f"🧩 示例: {preview}")
        print(f"📂 已保存至: {final_output}")
        return {"count": len(extracted_data), "output": final_output}

    except Exception as e:
        print(f"💥 发生错误: {e}")
        return {"count": 0, "output": None}


if __name__ == "__main__":
    FILE_TO_SEARCH = 'particle_emitters_old.json'

    print("--- 特效双重搜索提取工具 ---")
    print("提示: 多关键词可用逗号分隔；正则用 re:pattern")
    k_in = input("1. 输入特效名关键词 (直接回车跳过): ").strip()
    s_in = input("2. 输入SWF/Name关键词 (例如 effects_brawler): ").strip()

    if k_in or s_in:
        extract_effects_advanced(FILE_TO_SEARCH, k_in, s_in)
    else:
        print("未输入任何搜索条件。")
