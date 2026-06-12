# Talos Pipeline Note

## Muc tieu cuoi

Talos la app local dong vai tro tool server cho Codex, giup Codex lam viec voi cac IDE/app ben ngoai VSCode. Truoc mat Talos tap trung vao Arduino IDE: nhan dien sketch dang mo, tim dung sketch folder, doc/sua file, detect board, verify code trong sandbox, va tao vong lap debug co the lap lai.

Muc tieu ngan gon:

```text
Talos = local bridge giua Codex va cac IDE/app khac, bat dau voi Arduino IDE.
```

## Vi tri hien tai

- Detect Arduino IDE dang chay.
- Detect nhieu sketch `.ino` dang mo.
- Truy nguoc sketch folder that khi sketch da duoc luu.
- Bo qua stale process path khi file cu da dong.
- Khong coi folder tam `.arduinoIDE-unsaved...` la workspace hop le.
- Detect board/FQBN tu Arduino language server.
- Verify sandbox bang `arduino-cli`.
- Build va load duoc native C DLL tai `native/bin/talos_native.dll`.
- UI da co theme, scroll, copy output, copy file list, va dashboard trang thai.

Danh gia pipeline:

```text
Stage 1 - Arduino detection stability: mostly usable, can keep refining.
Stage 2 - Verify output cleanup: current active step.
Stage 3 - Arduino file workflow: next major step after verify output is structured.
Stage 4 - Codex debug loop: depends on Stage 2 and Stage 3.
Stage 5 - Native C expansion: optional performance hardening.
Stage 6 - MATLAB: later, after Arduino is stable.
```

## Pipeline tiep theo

### 1. Arduino detection stability

- Giam latency khi mo/dong sketch.
- Lam ro trang thai unsaved sketch trong UI.
- Chi cho phep select/verify khi sketch co folder that.
- Tang do chinh xac mapping sketch voi board khi Arduino IDE mo nhieu cua so.

### 2. Verify output cleanup

- [x] Xoa ANSI escape code trong output.
- [x] Parse compile result thanh cac truong rieng:
  - status
  - memory usage
  - used libraries
  - used platform
  - errors/warnings co ban
- [ ] Hien thi loi compile theo file/line trong UI neu co.

### 3. Arduino file workflow

- Them panel/doc file editor cho `.ino`, `.cpp`, `.h`.
- Cho phep doc/sua/luu file trong sketch folder.
- Dam bao moi thao tac file bi scope trong workspace, khong thoat ra ngoai folder sketch.

### 4. Codex debug loop

- Verify sandbox.
- Neu fail, parse loi thanh danh sach file/line/message.
- Dua context loi va file lien quan cho Codex.
- Sua file.
- Verify lai.

### 5. Native C expansion

- Hien native C dang xu ly window title va extract `.ino` name.
- Co the chuyen them process/window detection sang C de giam phu thuoc PowerShell/CIM.
- Muc tieu la detection nhanh hon, it delay hon, on dinh hon tren Windows.

### 6. MATLAB sau khi Arduino on dinh

- Detect MATLAB dang chay.
- Detect current folder/script.
- Doc/sua file MATLAB.
- Chay script/command trong sandbox hoac runtime co kiem soat.

## Nguyen tac phat trien

- Uu tien Arduino truoc, MATLAB sau.
- Khong coi unsaved/temp sketch la workspace hop le.
- Moi verify phai chay tren sandbox copy, khong build truc tiep tren folder goc.
- UI phai cho copy output/context de debug nhanh voi Codex.
- Native C chi nen ganh phan can toc do/he thong; Python giu vai tro bridge/API.
