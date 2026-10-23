# share_skill

ชุด skill สำหรับ AI agent (Claude Code, Codex, ChatGPT, Claude app) ที่เปลี่ยนภาพอ้างอิงเป็นโมเดล 3D ใน Blender ที่แก้ต่อได้

| เริ่มตรงนี้ | เนื้อหา |
|---|---|
| [modeling/WORKFLOW.md](modeling/WORKFLOW.md) | ใช้งานอย่างไร: 5 ขั้น, ตัวอย่างคำสั่ง, เช็กลิสต์ตรวจงาน, วิธีให้ feedback |
| [modeling/setup/SETUP.md](modeling/setup/SETUP.md) | ติดตั้งสำหรับ Claude Code / Codex / ChatGPT / Claude app, Blender MCP, GPU |
| [modeling/README.md](modeling/README.md) | รายละเอียดแต่ละ skill, ขอบเขต, โครงสร้างไฟล์, การแพ็ก ZIP |

ติดตั้งเร็ว:

```powershell
cd modeling\setup
.\install.ps1 all      # หรือ ./install.sh all บน macOS/Linux
.\install.ps1 smoke    # ทดสอบกับ Blender
```
