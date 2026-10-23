# Workflow

ติดตั้งตาม [setup/SETUP.md](setup/SETUP.md) ก่อน ส่วนรายละเอียดของแต่ละ skill และไฟล์ที่ได้อยู่ใน [README.md](README.md)

```text
ภาพ ──① reference-to-concept──► concept ──② concept-to-model-prompt──► prompt package
    ──③ model-prompt-to-blender──► โมเดล ──► ตรวจ ──④ blender-detail-repair──► ⑤ blender-model-verify
```

## ①–② Concept และ prompt

แนบภาพแล้วสั่ง:

```text
ใช้ $reference-to-concept วิเคราะห์ภาพที่แนบ ชื่อชิ้นงาน: forest-lantern
ขาที่เป็นคู่ให้สมมาตร ตาอยู่กลางลำตัว
ผ่าน QA แล้วใช้ $concept-to-model-prompt ต่อ แพ็กเป็น forest-lantern_artifact.zip
เก็บงานที่ <workdir>
```

ตรวจก่อนไปขั้น ③:

- [ ] `concept_sheet.png` มีภาพขยายส่วนสำคัญ และอ่านรายละเอียดออก
- [ ] ทุก feature ใน `details.md` มีจำนวน ขนาด ตำแหน่ง และบอกว่าเป็น mesh หรือ texture
- [ ] ระบุชัดว่าอะไรสมมาตร อะไรต้องอยู่กลาง
- [ ] ซ้าย-ขวาของภาพ ตัวแบบ และแกน X ตรงกัน
- [ ] ตัวเลขใน prompt ไม่ขัดกับ concept

ไม่ผ่านข้อไหนให้แก้ที่ ①–② ก่อน แก้ prompt เร็วกว่าแก้โมเดล

## ③ สร้างโมเดล

เปิด Blender กด Start MCP Server แล้วสั่ง:

```text
ใช้ $model-prompt-to-blender กับ <workdir>/forest-lantern
```

ลำดับงาน: preflight → blockout เทียบ silhouette → ต้นแบบชิ้นซ้ำและตรวจสมมาตร → รายละเอียด mesh เทียบ close-up → วัสดุ → เรนเดอร์ภาพตรวจและเขียน `verification.md`

ผลอยู่ใน `model_output/` ภาพ hero ต้องสั่งเพิ่มเอง

## ④ ตรวจและให้ feedback

ดูตามลำดับ:

1. ภาพ clay เทียบภาพอ้างอิง: มวล สัดส่วน ท่า
2. ภาพ front และ top: สมมาตร ตำแหน่งกลาง
3. ภาพ details และภาพเทียบ close-up
4. `verification.md`: Gates, Feature coverage (`fail`, `not_verified`), Fidelity differences

สั่งแก้ทีละ 1–2 เรื่อง บอกชิ้น ต่างอย่างไร และเทียบกับภาพไหน:

```text
ใช้ $blender-detail-repair: ขาทั้ง 4 ไม่สมมาตรเหมือน concept sheet
ใช้ $blender-detail-repair: ขาเรียบไปเมื่อเทียบ reference เพิ่มแผ่นเกราะ รอยต่อ น็อต ข้อต่อ
```

## ⑤ ตรวจและเรนเดอร์ใหม่

```text
ใช้ $blender-model-verify กับ <workdir>/forest-lantern/model_output
```

skill ใช้ GPU ให้อัตโนมัติ ครั้งแรกที่ใช้ OptiX จะช้าราว 45 วินาที ถ้า MCP แจ้ง timeout ระหว่างเรนเดอร์ ไม่ใช่ error

## ตัวอย่าง: orange-orb-walker

โค้ดและรายงานอยู่ใน [model-prompt-to-blender/examples/orange-orb-walker/](model-prompt-to-blender/examples/orange-orb-walker/README.md)

| รอบ | feedback | แก้ | ควรระบุไว้ใน prompt ตั้งแต่แรก |
|---|---|---|---|
| 1 | — | blockout, 13 แผง, วัสดุ | — |
| 2 | ขาไม่สมมาตร ตาไม่อยู่กลางและไม่ลึก | ขาสมมาตร, ตาอยู่กลาง ลึก 0.09 | เจตนาสมมาตรและตำแหน่งกลาง |
| 3 | ขาเรียบไป | เกราะมีสัน, รอยต่อ, น็อต, ข้อต่อ | เทียบ close-up กับ crop |
| 4 | body ขาดรายละเอียด | 21 แผง, แผ่นซ้อน, ช่องมีกรอบ, หมุด | จำนวนแผงและรอยต่อเป็นตัวเลข |

## ข้อควรรู้

- ใส่ตัวเลข (จำนวน ขนาด ตำแหน่ง) แทนคำกว้าง ๆ อย่าง "small details"
- ถ้าต้องการภาพ hero, rig หรือ export ให้บอกตั้งแต่แรก
- `.blend` เก่าเก็บเป็น `.blend1` และ build script เวอร์ชันก่อนก็เก็บไว้ ย้อนกลับได้
- ปัญหาที่พบบ่อยดูท้าย [README.md](README.md)
