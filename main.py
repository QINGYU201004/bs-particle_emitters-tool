import os
import sys

# 确保导入 lib 目录下的脚本
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

try:
    import fix
    import old
    import add
    import search
    import sc_extract
    import csv_name_extract
    from language import LANG_DATA
except ImportError as e:
    print(f"Error: Module import failed: {e}")
    sys.exit(1)

current_lang = None


def get_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 40


def clear_screen():
    os.system('clear')


def pause(L):
    input(f"\n{L['press_enter']}")


def ask_file(L, default_name):
    return input(f"{L['src_file']} ({default_name}): ").strip() or default_name


def ask_out_file(L, default_name):
    return input(f"{L['out_file']} ({default_name}): ").strip() or default_name


def init_language():
    global current_lang
    clear_screen()
    width = get_width()
    base_lang = LANG_DATA.get('en', {})

    print("=" * width)
    print(base_lang.get("lang_title", "Select Language | 选择语言 | Выберите язык").center(width))
    print("=" * width)
    print("[1] English")
    print("[2] 中文")
    print("[3] Русский")
    print("=" * width)

    while True:
        choice = input(base_lang.get("lang_prompt", ">>> ")).strip()
        if choice == '1':
            current_lang = 'en'
            return
        if choice == '2':
            current_lang = 'zh'
            return
        if choice == '3':
            current_lang = 'ru'
            return


def show_menu():
    width = get_width()
    clear_screen()
    L = LANG_DATA[current_lang]

    divider = "=" * width

    print("=" * width)
    print(L["title"].center(width))
    print("=" * width)
    print(L["opt1"])
    print(L["opt2"])
    print(L["opt3"])
    print(L["opt4"])
    print(L["opt6"])
    print(L["opt7"])
    print(divider)
    print(L["opt5"])
    print(L["opt0"])
    print(divider)


def switch_lang():
    global current_lang
    L = LANG_DATA[current_lang]
    print("-" * get_width())
    choice = input(L["lang_select"]).strip()
    if choice == '1':
        current_lang = 'en'
    elif choice == '2':
        current_lang = 'zh'
    elif choice == '3':
        current_lang = 'ru'


def do_fix_json(L):
    in_f = ask_file(L, 'particle_emitters.json')
    out_f = ask_out_file(L, 'particle_emitters_fixed.json')
    fix.robust_fix_and_sort(in_f, out_f)


def do_convert_old(L):
    in_f = ask_file(L, 'particle_emitters_fixed.json')
    out_f = ask_out_file(L, 'particle_emitters_old.json')

    if not os.path.exists(in_f):
        print(L['error'])
        return

    old.convert_file_to_old(in_f, out_f)
    print(f"{L['success']} {out_f}")


def do_search(L):
    src_label = L.get("search_src_file", "Source file")
    key_label = L.get("key_keyword", "Key keyword")
    swf_label = L.get("swf_keyword", "SC/SWF keyword")

    in_f = input(f"{src_label} (particle_emitters_old.json): ").strip() or 'particle_emitters_old.json'
    k = input(f"{key_label}: ").strip()
    s = input(f"{swf_label}: ").strip()
    search.extract_effects_advanced(in_f, k, s)


def do_merge(L):
    base_label = L.get("base_file", "Base file")
    patch_label = L.get("patch_file", "Patch file")

    base = input(f"{base_label}: ").strip()
    patch = input(f"{patch_label}: ").strip()
    out = input(f"{L['out_file']}: ").strip()
    if base and patch and out:
        add.physical_merge_safe(base, patch, out)


def do_extract_sc(L):
    src_label = L.get("sc_src_file", "Source file")
    out_label = L.get("sc_out_file", "Output file")

    in_f = input(f"{src_label} (particle_emitters_old.json): ").strip() or "particle_emitters_old.json"
    out_f = input(f"{out_label} (auto): ").strip()
    sc_extract.extract_movieclip_sc_names(in_f, out_f or None)


def do_extract_csv_names(L):
    csv_label = L.get("csv_src_file", "CSV file")
    json_label = L.get("name_json_src_file", "JSON file")
    out_label = L.get("name_json_out_file", "Output file")

    csv_path = input(f"{csv_label} (effects.csv): ").strip() or "effects.csv"
    json_path = input(f"{json_label} (particle_emitters_old.json): ").strip() or "particle_emitters_old.json"
    out_path = input(f"{out_label} (auto): ").strip()
    csv_name_extract.extract_particle_emitter_names(csv_path, json_path, out_path or None)


def run_action(choice, L):
    actions = {
        '1': do_fix_json,
        '2': do_convert_old,
        '3': do_search,
        '4': do_merge,
        '5': lambda _L: switch_lang(),
        '6': do_extract_sc,
        '7': do_extract_csv_names,
    }

    if choice == '0':
        clear_screen()
        return False

    action = actions.get(choice)
    if not action:
        input(f"{L.get('invalid_input', 'Invalid input.')} {L['press_enter']}")
        return True

    try:
        action(L)
    except Exception as e:
        print(f"{L.get('runtime_error', 'Error')}: {e}")

    if choice != '5':
        pause(L)
    return True


def main():
    init_language()

    while True:
        show_menu()
        L = LANG_DATA[current_lang]
        choice = input(L["input_choice"]).strip()
        if not run_action(choice, L):
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
