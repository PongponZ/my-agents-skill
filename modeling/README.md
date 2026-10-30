# Reference → Prompt skills

ชุดนี้มี main skill 1 ตัวคุม 2 stage skills สำหรับเปลี่ยนภาพอ้างอิงเป็น prompt package พร้อมส่งต่อให้ workflow สร้างโมเดล

| Skill | ทำอะไร |
|---|---|
| `reference-to-prompt` | เรียกใช้งานครั้งเดียว คุมขั้น concept → prompt จนได้ ZIP |
| `reference-to-concept` | วิเคราะห์ภาพ สร้าง concept sheet และหลักฐานรายละเอียด |
| `concept-to-model-prompt` | แพ็ก main prompt และภาพ reference พร้อม prompt รายส่วนเป็น `<name>_artifact.zip` |

วิธีใช้อยู่ใน [WORKFLOW.md](WORKFLOW.md) วิธีติดตั้งอยู่ใน [setup/SETUP.md](setup/SETUP.md)

## ติดตั้ง

```powershell
cd setup
.\install.ps1 all       # Claude Code, Codex และ ZIP สำหรับอัปโหลด
.\install.ps1 check     # ตรวจ main skill, 2 stage skills และลิงก์
```

| Target | ปลายทาง |
|---|---|
| `claude-code` | `~/.claude/skills/` |
| `codex`, `chatgpt-desktop` | `~/.agents/skills/` (เพิ่ม `--codex-legacy` สำหรับ `~/.codex/skills/`) |
| `claude-app`, `chatgpt-web` | `setup/dist/<platform>/<skill>.zip` สำหรับอัปโหลด |

แก้ source แล้วรันคำสั่งเดิมซ้ำ ของเดิมจะถูกสำรองไว้ที่ `~/.skill_backups/`

เริ่มด้วย `$reference-to-prompt` พร้อมภาพอ้างอิง main skill จะทำสองขั้นต่อกันและส่ง ZIP เมื่อผ่านการตรวจ หากติดตั้งเฉพาะ main skill ตัวติดตั้งจะรวมสอง stage ไว้ภายใน จึงใช้แยกได้โดยไม่ต้องติดตั้ง skill อื่นเพิ่ม

## ขอบเขต

ชุดนี้จบที่ concept และคำสั่งสร้างโมเดล ไม่เปิด Blender หรือสร้างไฟล์โมเดลเอง Prompt ระบุรูปทรง สัดส่วน รายละเอียด mesh, topology, วัสดุ/texture และเกณฑ์ตรวจที่ผู้สร้างโมเดลนำไปใช้ต่อได้

ทุก feature คง ID, แหล่งอ้างอิง, สถานะ observed/inferred/proposed, วิธีทำ mesh หรือ texture และเกณฑ์ตรวจไว้ กติกากลางอยู่ใน main; รายละเอียดเฉพาะส่วนอยู่ข้างภาพของส่วนนั้น

## ไฟล์ที่ได้

```text
<name>/
  main_prompt.md
  parts/
    00-overview/
      prompt.md
      reference.png
    body/
      prompt.md
      reference.png
    legs/
      prompt.md
      reference.png
<name>_artifact.zip
```

จำนวน part ปรับตามชิ้นงาน ZIP มีเฉพาะ main + part prompts และภาพที่ลิงก์ใช้ เอกสาร analysis, QA และประวัติสร้าง concept เก็บเป็นไฟล์ทำงาน ไม่ติด ZIP

ภาพ reference แรกใน `00-overview` แสดงตัวแบบเต็มในมุม **FRONT, TOP, SIDE** ที่สเกลและท่าตรงกัน หากภาพต้นทางรวมหลายส่วน จะสร้างภาพใหม่แยกแต่ละ part จาก reference เดิมแทนการ crop ภาพ พร้อมตรวจว่ารูปทรงและจุดเชื่อมต่อสอดคล้องกับภาพรวม

ใช้ prompt ภาษาเดียวเป็นค่าเริ่มต้น ผู้รับงานอ่าน main กับ overview ก่อน แล้วโหลดเฉพาะ part ที่กำลังทำและ dependency ที่จำเป็น คำสั่งใน main ระบุให้บันทึกความคืบหน้าและกลับมาอ่านส่วนที่ต้องใช้หลัง context ถูกย่อ

## แพ็ก ZIP เอง

```powershell
python concept-to-model-prompt/scripts/package_artifact.py --project <workdir>/<name> --output-dir <workdir>/packages
python -B -m unittest discover -s concept-to-model-prompt/scripts -p "test_*.py"
```

ชื่อโฟลเดอร์ project ใช้ตัวพิมพ์เล็ก ASCII คั่นด้วยขีด หรือกำหนด `--name <slug>` ตัวแพ็กตรวจลิงก์ ไฟล์ หัวข้อ prompt รายส่วน โครงสร้าง PNG และ bytes ใน ZIP โดยไม่เพิ่ม manifest ผู้เขียนยังต้องตรวจภาพและความครบของ feature เอง ถ้ามี ZIP ชื่อเดียวกันอยู่แล้วจะหยุด

หากมี handoff แบบเก่า ให้กลั่นข้อมูลเป็น main + parts ก่อนแพ็ก โดยคงไฟล์เดิมไว้

## แก้ปัญหา

| อาการ | ทางแก้ |
|---|---|
| agent ไม่เห็น skill | ดู [setup/SETUP.md](setup/SETUP.md) |
| ไม่มีเครื่องมือสร้างภาพ | ขั้น concept เก็บ analysis ไว้และรายงาน `blocked_image_generation` |
| แพ็ก ZIP ไม่ผ่าน | แก้ไฟล์หรือลิงก์ตามข้อความผิดพลาด แล้วตรวจภาพและ prompt อีกครั้ง |
