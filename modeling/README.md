# Modeling skills

5 skill สำหรับเปลี่ยนภาพอ้างอิงเป็นโมเดล Blender ที่แก้ต่อได้

| Skill | ทำอะไร | ใช้ Blender |
|---|---|---|
| `reference-to-concept` | วิเคราะห์ภาพ ได้ `concept_sheet.png`, `analysis.json`, `details.md`, `detail_crops/` | ไม่ |
| `concept-to-model-prompt` | เขียน prompt ไทย/อังกฤษ และ `build_spec.json` แล้วแพ็กเป็น `<name>_artifact.zip` | ไม่ |
| `model-prompt-to-blender` | สร้างโมเดลจาก prompt package ผ่าน Blender MCP | ใช้ |
| `blender-detail-repair` | แก้รายละเอียดตาม feedback | ใช้ |
| `blender-model-verify` | ตรวจ topology และ symmetry, เรนเดอร์ภาพตรวจ, เขียน `verification.md` | ใช้ |

วิธีใช้อยู่ใน [WORKFLOW.md](WORKFLOW.md) วิธีติดตั้งแต่ละแพลตฟอร์มอยู่ใน [setup/SETUP.md](setup/SETUP.md)

## ติดตั้ง

```powershell
cd setup
.\install.ps1 all     # Claude Code, Codex, ไลบรารี Blender, ZIP สำหรับ Claude app และ ChatGPT web
.\install.ps1 smoke   # ทดสอบใน Blender ต้องได้ SMOKE_OK และ NO_SHELL_OK
```

| Target | ติดตั้งที่ |
|---|---|
| `claude-code` | `~/.claude/skills/` |
| `codex`, `chatgpt-desktop` | `~/.agents/skills/` (Codex รุ่นเก่าเพิ่ม `--codex-legacy`) |
| `claude-app`, `chatgpt-web` | `setup/dist/<platform>/<skill>.zip` แล้วอัปโหลดเอง |
| `blender` | `<Blender user>/scripts/modules/` |

แก้ source แล้วรันคำสั่งเดิมซ้ำ ของเดิมจะถูกสำรองไว้ที่ `~/.skill_backups/`

## ขอบเขต

- **ทำ:** รูปทรง สัดส่วน รายละเอียด mesh, topology, วัสดุและ texture แบบ procedural, ภาพตรวจ (ortho, clay, close-up) และรายงาน
- **ไม่ทำ ถ้าไม่สั่ง:** ฉาก แท่นโชว์ HDRI ชุดไฟโชว์ hero render, rig, animation, export
- **ค่าเริ่มต้น:** static mesh ไม่เดาขนาดจริง งบ polygon หรือ rig จากภาพ

## กฎหลัก

- ทุก feature มี ID, สถานะ `observed` / `inferred` / `proposed`, แหล่งแบบ, วิธีทำ (mesh หรือ texture) และเกณฑ์ตรวจ
- ชิ้นที่เป็นคู่สร้างจากต้นแบบเดียวแล้ว mirror และวัดค่าความต่างก่อนไปต่อ ความต่างจาก perspective ไม่นับเป็นหลักฐานว่าขนาดต่างกัน
- Phase A (mesh) ต้องผ่านการเทียบ close-up กับ crop ก่อนเข้า Phase B (วัสดุ)
- ส่วนที่ตรวจไม่ได้ให้ระบุ `not_verified` ห้ามนับว่าผ่านเพราะ object ครบ

prompt มี 7 หัวข้อ: Geometry & Proportions, Reference Fidelity & Design Decisions, Components & Mesh Details, Topology & Assembly Quality, Materials & Textures, Modeling Progression, Verification & Delivery

## ไฟล์ที่ได้

```text
<name>/                          จาก skill 1–2
  references/, detail_crops/
  concept_sheet.png, concept_sheet_prompt.md
  analysis.json, analysis.md, details.md
  model_prompt.th.md, model_prompt.en.md, build_spec.json
  concept_qa.md, prompt_qa.md, handoff.md, usage.th.md, usage.en.md
<name>_artifact.zip              ไฟล์ด้านบน + manifest.json (ขนาดและ SHA-256)

<name>/model_output/             จาก skill 3–5
  <name>_blockout.blend/.png, <name>_detailed.blend, <name>_final.blend
  <name>_front/right/rear/top.png, <name>_clay.png, <name>_details.png
  verification.md
```

## แพ็ก ZIP เอง

```powershell
python concept-to-model-prompt/scripts/package_artifact.py --project <workdir>/<name> --output-dir <workdir>/packages
python -B -m unittest discover -s concept-to-model-prompt/scripts -p "test_*.py"   # ทดสอบตัวแพ็ก
```

ตัวแพ็กตรวจ schema, feature coverage, prompt สองภาษา, สถานะ QA และ hash แต่ไม่ได้ตรวจว่าภาพเหมือน reference หรือคำแปลตรงกัน ถ้ามี ZIP ชื่อเดียวกันอยู่แล้วจะหยุด

งานเก่าที่ใช้ schema 1–2 แพ็กไม่ได้ ให้ทำขั้น 1–2 ใหม่ในโฟลเดอร์ใหม่ อย่าแก้แค่เลข `schema_version`

## แก้ปัญหา

| อาการ | ทางแก้ |
|---|---|
| agent ไม่เห็น skill | ดู [setup/SETUP.md](setup/SETUP.md) |
| สั่ง Blender ไม่ได้ | เปิด Blender แล้วกด Start MCP Server และตั้ง MCP `blender` ใน client |
| MCP timeout ระหว่างเรนเดอร์ | Blender ยังทำงานอยู่ รอ marker file อย่าสั่งเรนเดอร์ซ้ำ |
| เรนเดอร์ช้า | ดู `Cycles device` ใน `verification.md` ถ้าเป็น CPU ให้ตรวจไดรเวอร์ GPU |
| รายละเอียดเรียบกว่า reference | ใช้ `$blender-detail-repair` ระบุชิ้นและภาพอ้างอิง |
| แผงเกราะติดกัน | รอยต่อต้องปิดเป็นวง ดู `model-prompt-to-blender/references/pitfalls.md` |
| ไม่มีเครื่องมือสร้างภาพในขั้น 1 | skill จะเก็บ analysis ไว้และรายงาน `blocked_image_generation` |
