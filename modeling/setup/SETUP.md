# ติดตั้ง skill ชุด modeling (Claude Code · Codex · ChatGPT · Claude app)

ชุดนี้มี 5 skills: `reference-to-concept`, `concept-to-model-prompt`, `model-prompt-to-blender`, `blender-detail-repair` และ `blender-model-verify` วิธีใช้งานทั้ง pipeline อยู่ใน [../WORKFLOW.md](../WORKFLOW.md)

ตัวติดตั้ง `install_skills.py` ใช้แค่ Python standard library ทำงานได้บน Windows, macOS และ Linux
- **skill ครบในตัว:** skill ที่ใช้ไลบรารี Blender ร่วมกันจะได้สำเนาไฟล์ที่จำเป็นไปด้วย ติดตั้งแยกทีละตัวได้
- **สำรองของเดิมก่อนทับ:** ย้ายไปไว้ที่ `~/.skill_backups/<target>/`
- **ทดลองก่อนได้:** ใช้ `--dry-run` ดูก่อนว่าจะติดตั้งอะไรไปไหน ติดตั้งเฉพาะบางตัวด้วย `--skills a,b` และถอนด้วย `--uninstall`

## สิ่งที่ต้องมี

| สิ่งที่ต้องมี | ใช้ทำอะไร | หมายเหตุ |
|---|---|---|
| Python 3.10+ | ตัวติดตั้ง และตัวแพ็ก ZIP ของ skill ที่ 2 | |
| Blender 4.2 ขึ้นไป | skill ที่ 3–5 | ทดสอบกับ 5.2 |
| uv (`uvx`) + add-on **MCP for Blender** | ให้ agent สั่งงาน Blender | ขั้นตอนอยู่ในหัวข้อ Blender ด้านล่าง |
| Pillow และ numpy | `img_tools.py` (crop, overlay, contact sheet) | ไม่บังคับ ถ้าไม่มี skill จะใช้ `bl_images` ที่ทำงานใน Blender แทน |
| GPU (NVIDIA/AMD/Apple) | เรนเดอร์ Cycles เร็วขึ้นราว 5 เท่า | skill เลือก OptiX > CUDA > HIP > oneAPI > Metal ให้เอง ถ้าไม่มีจะใช้ CPU |

## แต่ละแพลตฟอร์มทำอะไรได้บ้าง

| แพลตฟอร์ม | Skill 1–2 (concept + prompt) | Skill 3–5 (Blender) | ติดตั้งด้วย |
|---|---|---|---|
| **Claude Code** | ✅ | ✅ ครบทุกขั้น (มี shell + Blender MCP บนเครื่อง) | `install claude-code` |
| **Codex CLI / IDE** | ✅ | ✅ ครบ (ตั้ง MCP ใน `~/.codex/config.toml`) | `install codex` |
| **ChatGPT desktop app** | ✅ | ✅ เมื่อเชื่อม Blender MCP ผ่านส่วน Codex ของแอป (ตรวจในแอปว่าเห็น skill) | `install chatgpt-desktop` |
| **Claude desktop app** | ✅ ต้องเปิด code execution | ⚠️ สร้างโมเดลได้ผ่าน MCP ที่ตั้งไว้ในแอป แต่ไม่มี shell บนเครื่อง จึงตรวจผ่าน Blender แทน (`bl_images`, `inspect_saved_blend`) ซึ่งเข้มงวดน้อยกว่า | `install claude-app` แล้วอัปโหลด ZIP |
| **claude.ai web / ChatGPT web** | ✅ (ตามแพ็กเกจที่ใช้) | ❌ เว็บเข้าถึง Blender บนเครื่องไม่ได้ | `install claude-app` / `install chatgpt-web` แล้วอัปโหลด ZIP |

## ติดตั้งเร็ว

```powershell
# Windows (PowerShell) ในโฟลเดอร์ share_skill\modeling\setup
.\install.ps1            # เมนูให้เลือก
.\install.ps1 all        # Claude Code + Codex + ไลบรารี Blender + ZIP สำหรับ Claude app / ChatGPT web
.\install.ps1 check      # ตรวจ frontmatter และลิงก์ของทุก skill และบอกว่าติดตั้งไว้ที่ไหนแล้ว
.\install.ps1 smoke      # ทดสอบไลบรารีใน Blender แยกโปรเซส (ต้องได้ SMOKE_OK และ NO_SHELL_OK)
```

```sh
# macOS / Linux
./install.sh all
```

## 1. Claude Code

```powershell
.\install.ps1 claude-code                               # ~/.claude/skills/<skill>  ใช้ได้ทุกโปรเจกต์
.\install.ps1 claude-code --project C:\work\my-project  # <project>\.claude\skills\<skill>  เฉพาะโปรเจกต์นั้น
claude mcp add --scope user blender -- uvx mcp-for-blender   # เชื่อม Blender MCP ครั้งเดียว
```

- เปิด `claude` ใหม่ แล้วพิมพ์ `/model-prompt-to-blender` หรือบอกงานตรง ๆ เช่น “อ่าน model_prompt.en.md แล้วสร้างโมเดล”
- ในเอกสาร skill อ้างตำแหน่ง skill ด้วย `${CLAUDE_SKILL_DIR}` ได้

## 2. Codex (CLI / IDE)

```powershell
.\install.ps1 codex                  # ~/.agents/skills/<skill>  (path ระดับผู้ใช้ตามเอกสาร Codex)
.\install.ps1 codex --codex-legacy   # ติดตั้งเพิ่มที่ ~/.codex/skills สำหรับ Codex เวอร์ชันเก่า
```

เพิ่ม Blender MCP ใน `~/.codex/config.toml`

```toml
[mcp_servers.blender]
command = "uvx"
args = ["mcp-for-blender"]
```

เรียกใช้ด้วย `$model-prompt-to-blender` หรือเปิดรายการด้วย `/skills` ไฟล์ `agents/openai.yaml` ของแต่ละ skill ใช้ตั้งชื่อที่แสดงและ prompt เริ่มต้น

## 3. ChatGPT

**Desktop app**
- ใช้ standalone skill จากโฟลเดอร์เดียวกับ Codex: `.\install.ps1 chatgpt-desktop`
- เปิดแอปใหม่ แล้วดูว่ามี skill ในแถบ **Skills** ด้านข้าง เรียกใช้ด้วย `@` หรือเลือกจากรายการ
- ถ้าจะใช้กับ Blender ต้องตั้ง MCP ตามหัวข้อ Codex

**Web**
- `.\install.ps1 chatgpt-web` จะสร้างไฟล์ `setup\dist\chatgpt\<skill>.zip`
- อัปโหลดที่หน้า **Skills** ของ ChatGPT (ชื่อเมนูเปลี่ยนตามเวอร์ชัน)
- แพ็กเกจที่ใช้ได้ (เช่น Business/Enterprise/Edu) และการเปิดสิทธิ์ของ admin เปลี่ยนตามนโยบาย OpenAI ให้ตรวจในหน้า help ล่าสุด
- บนเว็บใช้ได้เฉพาะ skill ที่ 1–2

## 4. Claude app (claude.ai และ Claude desktop)

1. `.\install.ps1 claude-app` จะได้ไฟล์ `setup\dist\claude-app\<skill>.zip` ในแต่ละ ZIP โฟลเดอร์ skill อยู่ชั้นบนสุดตามที่ Claude กำหนด
2. ไปที่ **Customize → Skills** (claude.ai/customize/skills) อัปโหลด ZIP ทีละไฟล์ แล้วเปิดใช้ ต้องใช้แพ็กเกจ Pro/Max/Team/Enterprise และเปิด code execution
3. ถ้าจะสร้างโมเดลจาก Claude desktop ให้เพิ่ม Blender MCP ในไฟล์ config ของแอป แล้วรีสตาร์ตแอป
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

   ```json
   {"mcpServers": {"blender": {"command": "uvx", "args": ["mcp-for-blender"]}}}
   ```

4. ติดตั้งไลบรารีลง Blender ด้วย (ข้อ 5) เพราะ skill ใน Claude app อยู่ใน sandbox ที่ Blender บนเครื่องมองไม่เห็น

## 5. Blender (ทำครั้งเดียวต่อเครื่อง)

```powershell
uvx mcp-for-blender install-addon   # ติดตั้ง/อัปเดต add-on
.\install.ps1 blender               # คัดลอก bl_*.py ไป scripts\modules ของ Blender ทุกเวอร์ชันที่พบ
.\install.ps1 blender --blender-version 5.2
```

- **เปิด MCP:** ใน Blender ไปที่ Preferences → Add-ons → เปิด “Interface: Blender MCP” แล้วกด Start MCP Server ในแถบ N และเปิด Blender ทิ้งไว้ระหว่างที่ agent ทำงาน
- **ไลบรารี:** หลังติดตั้ง Blender จะ `import bl_build` ได้ทันทีโดยไม่ต้องตั้ง path ใช้ได้กับทุก client
- **GPU:** skill เปิด GPU ให้ตอนเรนเดอร์และไม่บันทึกลง Preferences ถ้าจะตั้งถาวรเอง ให้ไปที่ Preferences → System → Cycles Render Devices → OptiX/CUDA/HIP แล้วตั้ง Render Properties → Device → GPU Compute

## ตรวจหลังติดตั้ง

```powershell
.\install.ps1 check
.\install.ps1 smoke --blender "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
```

- `check` ตรวจชื่อ (ตัวพิมพ์เล็กและ `-` ยาวไม่เกิน 64 ตัว ตรงกับชื่อโฟลเดอร์), description ไม่เกิน 1024 ตัวอักษร, `SKILL.md` ยาวไม่เกิน 500 บรรทัด และลิงก์ในเอกสาร
- `smoke` สร้างโมเดลเล็กใน Blender แยกโปรเซส ทดสอบการแบ่งแผงเกราะ ขาสมมาตร วัสดุ การเรนเดอร์ GPU/CPU และเครื่องมือภาพ ไม่แตะ Blender ที่เปิดอยู่

## อัปเดตและถอนการติดตั้ง

- **อัปเดต:** แก้ source ใน `share_skill\modeling` แล้วรันคำสั่งติดตั้งเดิมซ้ำ ของเก่าจะถูกย้ายไป `~/.skill_backups/` สำหรับ Claude app และ ChatGPT web ให้อัปโหลด ZIP ใหม่ทับ
- **ถอนการติดตั้ง:** `.\install.ps1 claude-code --uninstall` (ใช้ได้กับ codex, chatgpt-desktop และ blender ด้วย)

## แก้ปัญหา

| อาการ | ทางแก้ |
|---|---|
| client ไม่เห็น skill | รีสตาร์ต client, ตรวจ path ปลายทาง (Codex เวอร์ชันเก่าใช้ `--codex-legacy`), รัน `check` |
| อัปโหลด ZIP ไม่ผ่าน | ใช้ ZIP จากตัวติดตั้งเท่านั้น (โฟลเดอร์ต้องอยู่ชั้นบนสุด) และเปิด code execution |
| agent สั่ง Blender ไม่ได้ | ตรวจว่า Blender เปิดอยู่และกด Start MCP Server แล้ว และ client ตั้ง MCP `blender` (`uvx mcp-for-blender`) แล้ว |
| `import bl_build` ไม่เจอใน Blender | รัน `install.ps1 blender` แล้วรีสตาร์ต Blender หรือให้ agent ใช้ `sys.path` / bootstrap ตาม SKILL.md |
| เรนเดอร์ช้า | ดูบรรทัด `Cycles device:` ใน log ถ้าเป็น CPU ให้ตรวจไดรเวอร์ GPU การเรนเดอร์ OptiX ครั้งแรกในเครื่องใช้ราว 45 วินาที |
| MCP แจ้ง timeout ตอนเรนเดอร์ | เป็นเรื่องปกติ Blender ยังทำงานต่อ skill จะรอ marker file เอง ห้ามสั่งเรนเดอร์ซ้ำ |

## ที่มาของข้อมูลการติดตั้ง

- Claude custom skills (โครงสร้าง ZIP, Customize → Skills, `${CLAUDE_SKILL_DIR}`): https://claude.com/docs/skills/how-to
- Agent Skills specification: https://agentskills.io/specification
- Codex skills (ตำแหน่ง `.agents/skills`, `agents/openai.yaml`, การเรียก `$skill`): https://learn.chatgpt.com/docs/build-skills
- ChatGPT skills (help center): https://help.openai.com/en/articles/20001066-skills-in-chatgpt

เมนูและเงื่อนไขของแต่ละแพลตฟอร์มเปลี่ยนได้ ถ้าขั้นตอนในแอปไม่ตรง ให้ยึดลิงก์ข้างบนเป็นหลัก
