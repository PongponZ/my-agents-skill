# ติดตั้ง skill ชุด reference → prompt

ชุดนี้มี main skill `reference-to-prompt` และ stage skills `reference-to-concept`, `concept-to-model-prompt` วิธีใช้อยู่ใน [WORKFLOW.md](../WORKFLOW.md)

ตัวติดตั้งใช้ Python 3.10+ และ standard library บน Windows, macOS และ Linux การสร้าง concept ต้องมีเครื่องมือสร้างภาพใน agent ที่ใช้งาน ส่วนชุดนี้ไม่ต้องติดตั้ง Blender, MCP หรือไลบรารีโมเดล

## ติดตั้ง

```powershell
# Windows: เรียกจากโฟลเดอร์ setup
.\install.ps1                 # เมนูเลือกปลายทาง
.\install.ps1 all             # Claude Code + Codex + ZIP สองชุด
.\install.ps1 check           # ตรวจ source, สำเนาที่เตรียมติดตั้ง และลิงก์
```

```sh
# macOS / Linux
./install.sh all
```

| Target | สิ่งที่ตัวติดตั้งทำ |
|---|---|
| `claude-code` | คัดลอก main skill และ 2 stage skills ไป `~/.claude/skills/` |
| `codex`, `chatgpt-desktop` | คัดลอกไป `~/.agents/skills/` |
| `claude-app` | สร้าง `setup/dist/claude-app/<skill>.zip` |
| `chatgpt-web` | สร้าง `setup/dist/chatgpt/<skill>.zip` |
| `check` | ตรวจชื่อ, frontmatter, description และลิงก์ |
| `all` | ติดตั้ง Claude Code + Codex และสร้าง ZIP ทั้งสองปลายทาง |

ZIP แต่ละไฟล์มีโฟลเดอร์ skill อยู่ชั้นบนสุด ให้นำไปอัปโหลดในหน้าจัดการ skill ของแพลตฟอร์มที่รองรับ หลังติดตั้งในเครื่อง ให้เปิด client ใหม่หากยังไม่พบ skill

main skill รวมสำเนาสอง stage และ resources ที่ต้องใช้ใน `workflows/` โดยสร้างจาก source ล่าสุดตอนติดตั้งหรือแพ็ก จึงติดตั้งหรืออัปโหลดเฉพาะ `reference-to-prompt` ตัวเดียวเพื่อใช้งานครบ workflow ได้ ส่วน stage skills ยังเรียกแยกได้หากติดตั้งไว้

## ตัวเลือก

```powershell
.\install.ps1 claude-code --project C:\work\my-project
.\install.ps1 codex --codex-legacy
.\install.ps1 codex --skills reference-to-prompt
.\install.ps1 codex --skills concept-to-model-prompt
.\install.ps1 codex --dest C:\work\skills --dry-run
.\install.ps1 chatgpt-web --dest C:\work\skill-zips
```

- `--project`: ติดตั้ง Claude Code เฉพาะโปรเจกต์ที่ `<project>/.claude/skills/`
- `--codex-legacy`: ติดตั้งเพิ่มที่ `~/.codex/skills/`
- `--skills`: เลือกชื่อ skill คั่นด้วย comma; ค่าเริ่มต้นคือ main skill และ stage skills รวม 3 ตัว
- `--dest`: เปลี่ยนโฟลเดอร์ปลายทางสำหรับติดตั้งหรือ ZIP
- `--dry-run`: แสดงรายการก่อนติดตั้ง
- `--no-backup`: แทนที่สำเนาเดิมโดยไม่สำรอง

เรียก workflow ครบด้วย `$reference-to-prompt` หรือเลือกทำเฉพาะขั้นด้วย `$reference-to-concept` / `$concept-to-model-prompt` ใน client ที่รองรับ

## อัปเดตและถอนการติดตั้ง

รันคำสั่งติดตั้งเดิมซ้ำเพื่ออัปเดต สำเนาเดิมจะถูกย้ายไป `~/.skill_backups/<target>/` ก่อนแทนที่ สำหรับ ZIP ให้อัปโหลดไฟล์ใหม่ด้วยตนเอง

ถอนทั้งชุดหรือเลือกเฉพาะตัวจากปลายทางในเครื่อง:

```powershell
.\install.ps1 codex --uninstall
.\install.ps1 claude-code --skills concept-to-model-prompt --uninstall
```

ตัวติดตั้งจัดการเฉพาะ 3 skill ในชุดปัจจุบัน ไม่ลบ skill อื่นที่เคยติดตั้งไว้

## ตรวจหลังแก้ source

```powershell
python -B install_skills.py check
python -B -m unittest discover -s . -p "test_*.py"
python -B -m unittest discover -s ../concept-to-model-prompt/scripts -p "test_*.py"
```

ถ้า client ไม่เห็น skill ให้ตรวจปลายทางที่ติดตั้งและเปิด client ใหม่ ถ้าอัปโหลด ZIP ไม่ผ่าน ให้ใช้ ZIP จากตัวติดตั้งและตรวจสิทธิ์นำเข้า skill ของแพลตฟอร์ม หาก agent ไม่มีเครื่องมือสร้างภาพ ขั้น concept จะรายงานข้อจำกัดและเก็บหลักฐานงานที่ทำไว้
