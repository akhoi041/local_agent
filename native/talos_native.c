#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wchar.h>
#include <wctype.h>

#define TALOS_TITLE_LIMIT 512

static int append_text(wchar_t *out, int out_len, int *used, const wchar_t *text) {
    int i = 0;
    if (!out || out_len <= 0 || !used || !text) return 0;
    while (text[i] && *used < out_len - 1) {
        out[*used] = text[i];
        (*used)++;
        i++;
    }
    out[*used] = L'\0';
    return text[i] == L'\0';
}

static int ends_with_ino(const wchar_t *text, int start, int end) {
    int len = end - start;
    if (len < 4) return 0;
    return towlower(text[end - 4]) == L'.'
        && towlower(text[end - 3]) == L'i'
        && towlower(text[end - 2]) == L'n'
        && towlower(text[end - 1]) == L'o';
}

static int arduino_marker_at(const wchar_t *title, int index) {
    const wchar_t *marker = L"Arduino IDE";
    int i = 0;
    while (marker[i]) {
        if (towlower(title[index + i]) != towlower(marker[i])) return 0;
        i++;
    }
    return 1;
}

static int valid_sketch_char(wchar_t ch) {
    return iswalnum(ch) || ch == L'_' || ch == L'.' || ch == L'-' || ch == L' ';
}

static int is_source_tab_suffix(const wchar_t *text, int start, int end) {
    static const wchar_t *suffixes[] = {
        L".ino", L".h", L".hpp", L".c", L".cc", L".cpp", L".cxx", L".s"
    };
    int suffix_index;
    for (suffix_index = 0; suffix_index < (int)(sizeof(suffixes) / sizeof(suffixes[0])); suffix_index++) {
        const wchar_t *suffix = suffixes[suffix_index];
        int suffix_len = (int)wcslen(suffix);
        int offset;
        if (end - start < suffix_len) continue;
        for (offset = 0; offset < suffix_len; offset++) {
            if (towlower(text[end - suffix_len + offset]) != towlower(suffix[offset])) break;
        }
        if (offset == suffix_len) return 1;
    }
    return 0;
}

static int append_inferred_ino_name(const wchar_t *title, wchar_t *out, int out_len, int *used, int count) {
    int i = 0;
    int end = -1;
    int start = 0;
    wchar_t name[TALOS_TITLE_LIMIT];
    int n = 0;

    while (title[i]) {
        if ((title[i] == L'|' || title[i] == L'-') && iswspace(title[i + 1])) {
            int marker = i + 1;
            while (iswspace(title[marker])) marker++;
            if (arduino_marker_at(title, marker)) {
                end = i;
                break;
            }
        }
        i++;
    }
    if (end <= 0) return count;

    while (start < end && iswspace(title[start])) start++;
    while (end > start && (iswspace(title[end - 1]) || title[end - 1] == L'-' || title[end - 1] == L'|')) end--;
    if (end <= start) return count;
    for (i = start; i + 2 < end; i++) {
        if (title[i] == L' ' && title[i + 1] == L'-' && title[i + 2] == L' ') {
            int tab_start = i + 3;
            if (is_source_tab_suffix(title, tab_start, end)) {
                end = i;
                while (end > start && iswspace(title[end - 1])) end--;
                break;
            }
        }
    }
    for (i = start; i < end; i++) {
        if (!valid_sketch_char(title[i])) return count;
    }
    if (ends_with_ino(title, start, end)) return count;

    for (i = start; i < end && n < TALOS_TITLE_LIMIT - 5; i++) {
        name[n++] = title[i];
    }
    name[n++] = L'.';
    name[n++] = L'i';
    name[n++] = L'n';
    name[n++] = L'o';
    name[n] = L'\0';
    if (count > 0) append_text(out, out_len, used, L"\n");
    append_text(out, out_len, used, name);
    return count + 1;
}

__declspec(dllexport)
int talos_extract_ino_names(const wchar_t *title, wchar_t *out, int out_len) {
    int count = 0;
    int used = 0;
    int i = 0;

    if (!out || out_len <= 0) return 0;
    out[0] = L'\0';
    if (!title) return 0;

    while (title[i]) {
        int start;
        int end;
        while (title[i] && !(iswalnum(title[i]) || title[i] == L'_' || title[i] == L'.' || title[i] == L'-' || title[i] == L' ')) {
            i++;
        }
        start = i;
        while (title[i] && (iswalnum(title[i]) || title[i] == L'_' || title[i] == L'.' || title[i] == L'-' || title[i] == L' ')) {
            i++;
        }
        end = i;
        while (start < end && iswspace(title[start])) start++;
        while (end > start && (iswspace(title[end - 1]) || title[end - 1] == L'-')) end--;
        if (ends_with_ino(title, start, end)) {
            wchar_t name[TALOS_TITLE_LIMIT];
            int j;
            int n = 0;
            for (j = start; j < end && n < TALOS_TITLE_LIMIT - 1; j++) {
                name[n++] = title[j];
            }
            name[n] = L'\0';
            if (count > 0) append_text(out, out_len, &used, L"\n");
            append_text(out, out_len, &used, name);
            count++;
        }
    }
    if (count == 0) {
        count = append_inferred_ino_name(title, out, out_len, &used, count);
    }
    return count;
}

struct enum_state {
    wchar_t *out;
    int out_len;
    int used;
    int count;
};

static BOOL CALLBACK enum_windows_proc(HWND hwnd, LPARAM lparam) {
    struct enum_state *state = (struct enum_state *)lparam;
    wchar_t title[TALOS_TITLE_LIMIT];
    int len;

    if (!IsWindowVisible(hwnd)) return TRUE;
    len = GetWindowTextLengthW(hwnd);
    if (len <= 0) return TRUE;
    GetWindowTextW(hwnd, title, TALOS_TITLE_LIMIT);
    if (!title[0]) return TRUE;

    if (state->count > 0) append_text(state->out, state->out_len, &state->used, L"\n");
    append_text(state->out, state->out_len, &state->used, title);
    state->count++;
    return TRUE;
}

__declspec(dllexport)
int talos_list_window_titles(wchar_t *out, int out_len) {
    struct enum_state state;
    if (!out || out_len <= 0) return 0;
    out[0] = L'\0';
    state.out = out;
    state.out_len = out_len;
    state.used = 0;
    state.count = 0;
    EnumWindows(enum_windows_proc, (LPARAM)&state);
    return state.count;
}
