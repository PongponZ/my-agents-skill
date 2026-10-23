# Workflow: จากภาพอ้างอิงถึงโมเดล Blender ด้วย skill ชุด modeling

คู่มือนี้อธิบายการใช้ 5 skills ต่อกันตั้งแต่ภาพเดียวจนได้ไฟล์ `.blend` ที่แก้ต่อได้ พร้อมภาพตรวจและรายงาน ถ้ายังไม่ได้ติดตั้ง ให้ทำตาม [setup/SETUP.md](setup/SETUP.md) ก่อน ขั้นที่รันจริงใช้เวลาประมาณ 5–10 นาที

```text
ภาพอ้างอิง
   │  ① $reference-to-concept      วิเคราะห์ภาพ → concept_sheet.png, analysis.json, details.md, detail_crops/
   ▼
แบบ + รายการรายละเอียด
   │  ② $concept-to-model-prompt   เขียนคำสั่ง → model_prompt.th/en.md, build_spec.json, <name>_artifact.zip
   ▼
prompt package
   │  ③ $model-prompt-to-blender   สร้างจริงใน Blender → .blend (blockout/detailed/final), ภาพตรวจ, verification.md
   ▼
โมเดล v1 ──► ผู้ใช้ตรวจ ──► ④ $blender-detail-repair (แก้ตาม feedback ทีละเรื่อง) ──┐
   ▲                                                                              │
   └──────────── ⑤ $blender-model-verify (render ใหม่ ตรวจ เขียนรายงาน) ◄─────────┘
```

| Skill | Input | Output หลัก | ต้องมี Blender ไหม |
|---|---|---|---|
| ① reference-to-concept | ภาพหลัก (และภาพเสริม) | `concept_sheet.png`, `analysis.json`, `details.md`, `detail_crops/` | ไม่ต้อง (ต้องสร้างภาพได้) |
| ② concept-to-model-prompt | โฟลเดอร์จาก ① | `model_prompt.*.md`, `build_spec.json`, ZIP | ไม่ต้อง |
| ③ model-prompt-to-blender | โฟลเดอร์หรือ ZIP จาก ② | `model_output/` ครบชุด | ต้อง (Blender MCP) |
| ④ blender-detail-repair | โมเดลจาก ③ + feedback | build script เวอร์ชันใหม่, ภาพ before/after, Revision ใน `verification.md` | ต้อง |
| ⑤ blender-model-verify | โมเดล | ภาพตรวจชุดใหม่, ผลตรวจ, `verification.md` | ต้อง |

---

## ขั้นที่ ①–② ทำแบบและ prompt

แนบภาพแล้วสั่งต่อกันในข้อความเดียวได้ (ดูตัวอย่างเต็มใน [README.md](README.md))

```text
ใช้ $reference-to-concept วิเคราะห์ภาพที่แนบ ชื่อชิ้นงาน: forest-lantern
รักษารูปทรง สัดส่วน รายละเอียดเด่น และการแบ่งวัสดุตามภาพ
ขาหรือชิ้นที่เป็นคู่ให้สมมาตร ส่วนที่อยู่กลางตัวให้อยู่กลางจริง
เมื่อผ่าน QA ให้ใช้ $concept-to-model-prompt ต่อ แล้วแพ็กเป็น forest-lantern_artifact.zip
เก็บงานที่ C:\Users\User\Desktop\projects\modeling_output
```

**ตรวจก่อนไปขั้นที่ ③ (ใช้เวลา 2 นาที แต่ประหยัดการแก้หลายรอบ)**
- [ ] `concept_sheet.png` มีภาพขยายของส่วนสำคัญ เช่น ขา ตา และเครื่องมือ และรายละเอียดอ่านออก
- [ ] ใน `details.md` และ `build_spec.json` ทุก feature มีจำนวน ขนาด ตำแหน่ง และบอกว่าเป็น mesh หรือ texture ไม่ใช่แค่คำว่า “มีรายละเอียด”
- [ ] เขียนเจตนาสมมาตรไว้ชัด เช่น “ขาคู่หน้า/หลังสมมาตร”
- [ ] ระบุตำแหน่งส่วนที่ต้องอยู่กลาง เช่น “แกนตาอยู่กึ่งกลางลำตัว”
- [ ] ซ้าย-ขวาของภาพ ตัวแบบ และแกน X ตรงกัน (ใช้ชิ้นที่ไม่สมมาตรเป็นจุดอ้างอิง เช่นเครื่องมือคนละแบบสองข้าง)
- [ ] ช่วงตัวเลขใน prompt ไม่ขัดกับ concept เช่นระยะกางขา

ข้อไหนไม่ผ่าน ให้สั่ง ① หรือ ② แก้ก่อน การแก้ใน prompt ถูกกว่าการแก้โมเดลหลายเท่า

---

## ขั้นที่ ③ สร้างโมเดล

เปิด Blender และกด Start MCP Server ไว้ก่อน แล้วสั่ง

```text
ใช้ $model-prompt-to-blender กับโฟลเดอร์:
C:\Users\User\Desktop\projects\modeling_output\forest-lantern
อ่าน model_prompt.en.md, build_spec.json, analysis.json, detail_crops และ concept_sheet.png
ทำตารางรายละเอียดก่อนขึ้นโมเดล เทียบ close-up ราย feature ก่อนเข้าขั้นวัสดุ
เก็บ .blend ทุก checkpoint, ภาพตรวจ, ภาพเทียบ และ verification.md ใน model_output
```

**สิ่งที่ skill ทำ** (ดูความคืบหน้าใน viewport ของ Blender ได้ตลอด)

1. **Preflight:** อ่านทุกไฟล์ ซูมดูภาพ และตรวจจุดขัดแย้งใน prompt บันทึกการตัดสินใจไว้ และถามเฉพาะเรื่องที่เปลี่ยนเอกลักษณ์ของงาน
2. **Blockout + reference match:** สร้างมวลหลัก แล้วซ้อน silhouette กับภาพอ้างอิงจนตรง บันทึก `*_blockout.blend/.png`
3. **ต้นแบบชิ้นซ้ำ + gate สมมาตร:** สร้างขาหรือแขนหนึ่งชุด เทียบกับ crop แล้ว mirror ด้วยพารามิเตอร์เดียวกัน วัดค่าความต่างเป็นตัวเลข
4. **Phase A รายละเอียด mesh:** สร้างทุก feature วาง close-up เทียบ crop แล้วแก้จนผ่าน ตรวจ topology และบันทึก `*_detailed.blend`
5. **Phase B วัสดุ:** วัสดุ procedural แยกโซน รอยสึก และแสงเรืองที่วัดความสว่างแล้ว
6. **ส่งมอบ:** เรนเดอร์ภาพตรวจด้วย GPU, เปิดไฟล์ซ้ำในโปรเซสแยก, ตรวจขนาดภาพ และเขียน `verification.md`

**ผลลัพธ์ใน `model_output/`**

```text
<name>_blockout.blend / _blockout.png       มวลหลักตรง reference
<name>_detailed.blend                       mesh ครบก่อนทำวัสดุ
<name>_final.blend                          ไฟล์สุดท้าย (scene แยก, กล้องตรวจครบ, บันทึกการตัดสินใจในไฟล์)
<name>_front/right/rear/top.png             orthographic สเกลเดียวกัน ท่าเดียวกัน
<name>_clay.png, <name>_details.png         clay + contact sheet ส่วนสำคัญ
ภาพเทียบ crop ↔ model ราย feature
verification.md                             gate, ตาราง coverage, symmetry, ค่าที่วัด, สิ่งที่ยังต่าง
```

ถ้า prompt ไม่ได้สั่ง hero/presentation จะได้เฉพาะภาพตรวจ ไม่มีชุดไฟโชว์ ถ้าต้องการภาพ hero ให้สั่งเพิ่มเอง

---

## ขั้นที่ ④ ตรวจและให้ feedback

**ดูอะไร (เรียงตามความสำคัญ)**
1. `REF_MATCH` หรือภาพ clay เทียบภาพอ้างอิง: มวล สัดส่วน ท่ายืน
2. ภาพ front และ top: ความสมมาตร และตำแหน่งส่วนที่ต้องอยู่กลาง
3. contact sheet หรือภาพเทียบ close-up: รายละเอียดราย component
4. ใน `verification.md` ดูหัวข้อ Gates, Feature coverage (มี fail หรือ not_verified ไหม) และ Fidelity differences

**เขียน feedback ให้ได้ผล:** ระบุ *ชิ้น* + *ต่างอย่างไร* + *ยึดภาพไหน* ทีละ 1–2 เรื่อง

```text
ใช้ $blender-detail-repair กับโมเดล forest-lantern
ขาทั้ง 4 ยังไม่สมมาตรเหมือน concept sheet — ทำให้สมมาตรซ้าย/ขวาและหน้า/หลัง
```

```text
ใช้ $blender-detail-repair: ตา (C04+C05) ยังไม่อยู่กลางลำตัว และความลึกยังไม่เท่าช่อง C04+C05 ใน concept
```

```text
ใช้ $blender-detail-repair: ขายังเรียบเกินไปเมื่อเทียบ reference — เน้นแผ่นเกราะ รอยต่อ น็อต และข้อต่อ
```

```text
ใช้ $blender-detail-repair: ตัว body อยากได้ detail เหมือน reference — แบ่งแผงเกราะ ช่องเว้า หมุด และรอยสึก
```

skill จะทำ crop → เรนเดอร์มุมเดียวกัน → gap list → แก้ใน build script → ตรวจซ้ำ → เรนเดอร์ใหม่ → เพิ่ม `Revision N` ในรายงาน และบอกตรง ๆ ว่ายังต่างตรงไหน

---

## ขั้นที่ ⑤ เรนเดอร์ใหม่ ตรวจ และส่งงาน

```text
ใช้ $blender-model-verify กับ C:\...\forest-lantern\model_output
ตรวจ topology และ symmetry, เรนเดอร์ภาพตรวจทั้งหมดใหม่, เปิด .blend ซ้ำแบบ background
ตรวจขนาดภาพ และอัปเดต verification.md
```

- เรนเดอร์ใช้ GPU อัตโนมัติ ดูชื่อการ์ดได้ในรายงาน เรนเดอร์ OptiX ครั้งแรกในเครื่องจะช้าราว 45 วินาที
- ถ้า MCP แจ้ง timeout ระหว่างเรนเดอร์ เป็นเรื่องปกติ skill จะรอ marker file เอง

---

## ตัวอย่างจริง: orange-orb-walker

ทำจาก prompt package หนึ่งชุด แล้วแก้อีก 3 รอบตาม feedback (โค้ดและรายงานอยู่ที่ [model-prompt-to-blender/examples/orange-orb-walker/](model-prompt-to-blender/examples/orange-orb-walker/README.md))

| รอบ | สิ่งที่ผู้ใช้ขอ | สิ่งที่เปลี่ยน | บทเรียน |
|---|---|---|---|
| Rev 1 | สร้างโมเดลตาม prompt | blockout ซ้อน silhouette 5 รอบ, 13 แผงเกราะ, วัสดุ, เรนเดอร์ | silhouette ตรงแล้ว แต่รายละเอียดยังน้อย |
| Rev 2 | ขาไม่สมมาตร, ตาไม่อยู่กลาง, ตาไม่ลึก | ขาสมมาตร, ตาอยู่กลาง, ขอบตาหลายชั้นลึก 0.09 | prompt ต้องระบุเจตนาสมมาตรและตำแหน่งกลาง |
| Rev 3 | ขาเรียบไป | เกราะเหลี่ยมมีสัน, รอยต่อ, แบ่งสีตัว V, น็อต, ข้อต่อแบบขั้น, ใบมีดเหลี่ยม | ต้องเทียบ close-up กับ crop ตั้งแต่แรก |
| Rev 4 | body อยาก detail เหมือน reference | แถบส้มเรียว, 21 แผง, แผ่นซ้อน, ช่องมีกรอบ, หมุด, รอยสึก | ต้องตรวจตัวเลขว่ารอยต่อแบ่งแผงจริง |

ถ้าทำตามเช็กลิสต์ขั้นที่ ①–② และ Phase A ตั้งแต่แรก รอบแก้ส่วนใหญ่จะไม่จำเป็น

---

## เคล็ดลับ

- **ให้ข้อมูลรายละเอียดเป็นรายการ:** เขียนเป็นชิ้น พร้อมจำนวน ขนาด ตำแหน่ง และ crop อ้างอิง แทนคำกว้าง ๆ อย่าง “restrained” หรือ “small details”
- **บอกเจตนาตรง ๆ:** สมมาตรหรือไม่ อะไรต้องอยู่กลาง และถ้าเป้าหมายขัดกันให้บอกว่าอะไรสำคัญกว่า เช่น สีอิ่มกับความสว่างของไฟ
- **แยกขอบเขต:** บอกว่าต้องการภาพตรวจหรือภาพโชว์ (hero) ต้องการ rig หรือ export หรือไม่
- **แก้ทีละเรื่อง:** feedback ทีละ 1–2 component ตรวจง่ายกว่าและ revision ไม่ปนกัน
- **ไฟล์เดิมไม่หาย:** checkpoint เก่าเป็น `.blend1` และ build script เวอร์ชันก่อนเก็บไว้เสมอ ย้อนกลับได้

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุและทางแก้ |
|---|---|
| agent มองไม่เห็น skill | ดู [setup/SETUP.md](setup/SETUP.md) หัวข้อแก้ปัญหา |
| สั่ง Blender ไม่ได้ | Blender ต้องเปิดอยู่และกด Start MCP Server แล้ว และ client ต้องตั้ง MCP `blender` |
| เรนเดอร์ช้า | ดู `Cycles device` ในรายงาน ถ้าเป็น CPU ให้ตรวจไดรเวอร์ GPU |
| สีซีดหรือแสงเรืองขาวเกินไป | skill ใช้ Khronos PBR Neutral และลดค่า emission แล้ว ถ้ายังไม่พอให้บอกว่าต้องการสีอิ่มหรือความสว่างมากกว่า |
| แผงเกราะติดกันผิด | รอยต่อต้องปิดเป็นวง skill จะตรวจจำนวนและขอบเขตแผงให้ ดู `model-prompt-to-blender/references/pitfalls.md` |
| รายละเอียดไม่ตรง | ใช้ ④ พร้อมบอก component และภาพอ้างอิง |
