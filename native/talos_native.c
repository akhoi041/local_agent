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
