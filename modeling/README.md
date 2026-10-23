# Modeling skills — จากภาพอ้างอิงสู่โมเดล Blender

ชุดนี้มี 5 skills สำหรับทำ concept, เขียน prompt และสร้างโมเดลจริงใน Blender โดยเน้น **mesh ที่ตรง reference พร้อมวัสดุและ texture อย่างละเอียด**

1. `$reference-to-concept` วิเคราะห์ภาพหลัก สร้าง `concept_sheet.png` และข้อกำหนดชิ้นส่วน/รายละเอียด/วัสดุ
2. `$concept-to-model-prompt` นำข้อมูลนั้นมาเขียน prompt ภาษาไทยและอังกฤษ แล้วแพ็กเป็น `<name>_artifact.zip`
3. `$model-prompt-to-blender` นำ prompt package ไปสร้างโมเดลจริงใน Blender ผ่าน Blender MCP โดยต้องผ่าน gate ตามลำดับ:
   blockout → reference match → ต้นแบบชิ้นซ้ำ + symmetry → รายละเอียด mesh + ตรวจ close-up → วัสดุ → ตรวจส่งมอบ
4. `$blender-detail-repair` วนแก้รายละเอียดตาม feedback เช่น “ขาเรียบไป”, “ลำตัวไม่เหมือน reference”, “ขาไม่สมมาตร”, “ตาไม่อยู่กลาง”
5. `$blender-model-verify` ตรวจ topology/symmetry, เรนเดอร์ภาพตรวจ, เปิดไฟล์ซ้ำแบบ background, ตรวจภาพ และเขียน/อัปเดต `verification.md`

**ZIP จาก skill ที่ 2 เป็นชุดข้อมูลกับ prompt ยังไม่ใช่โมเดลสำเร็จ** ขั้นสร้างจริงคือ skill ที่ 3 ซึ่งต้องเชื่อม Blender MCP

> **เริ่มที่นี่:** คู่มือใช้งานทั้ง pipeline อยู่ที่ [WORKFLOW.md](WORKFLOW.md) วิธีติดตั้งสำหรับ Claude Code / Codex / ChatGPT / Claude app อยู่ที่ [setup/SETUP.md](setup/SETUP.md)
> ติดตั้งเร็ว (Windows): `.\setup\install.ps1 all` แล้วทดสอบด้วย `.\setup\install.ps1 smoke`

## ขอบเขตเวอร์ชันนี้

| ทำ | ไม่รวมใน workflow นี้ |
|---|---|
| รูปทรง สัดส่วน หน้าตัด ความหนา ช่องเปิด และรายละเอียด mesh | ฉากเสริมเพื่อความสวยงามและแท่นโชว์ |
| การประกอบ จุดยึด topology และการแก้ข้อผิดพลาด | ชุดไฟ key/fill/rim และ HDRI |
| วัสดุละเอียด สี roughness, metallic และคุณสมบัติผิวตาม reference | กล้อง hero shot และ cinematic/beauty render |
| Texture, UV/mapping, ลวดลาย รอยสึก normal/bump และ displacement ที่เหมาะสม | การวนปรับแสงหรือ exposure เพื่อภาพนำเสนอ |
| วัสดุ emissive ที่เป็นส่วนของตัวแบบ | การใช้แสงหรือ texture กลบ geometry ที่ยังไม่ครบ |
| ภาพตรวจจาก viewport มุมตรง มุมข้าง มุมหลัง และ close-up | การถือว่าจำนวนชิ้นส่วนครบเท่ากับรายละเอียดครบ |

ใช้แสงมาตรฐานและพื้นหลังเรียบสำหรับตรวจงานได้ หากจับ viewport ไม่ได้ ใช้ภาพเรนเดอร์ตรวจแบบง่ายเท่าที่จำเป็น ถ้า reference เป็นอาคารหรือ environment ตัวฉากที่เป็นชิ้นงานยังอยู่ในขอบเขต

## เตรียมข้อมูล

ต้องมี primary reference อย่างน้อยหนึ่งภาพที่ agent เปิดดูได้ ถ้ามีหลายภาพ ให้ระบุภาพหลักและภาพเสริม

ข้อมูลที่ช่วยให้งานชัดเจน:
- ชื่อชิ้นงาน เช่น `forest-lantern`
- การใช้งาน สิ่งที่ต้องรักษา และการเปลี่ยนแบบที่ต้องการ
- ขนาดจริงถ้าทราบ งบรายละเอียดหรือ polygon ถ้ามี
- ข้อกำหนดวัสดุ/texture และโฟลเดอร์บันทึก
- การ export, rig, animation หรือพิมพ์ 3D ถ้าต้องการจริง

ค่าเริ่มต้นคือ static editable mesh พร้อมวัสดุและ texture ไม่สมมติหน่วยเมตร งบ polygon หรือ rig จากภาพเพียงอย่างเดียว

เครื่องมือ: skill แรกต้องดูภาพและสร้างภาพได้ ตัวแพ็กใช้ Python 3.10+ และ standard library การเขียน prompt ยังไม่ต้องเชื่อม Blender ส่วนขั้นสร้างจริงต้องมีเครื่องมือ Blender

## วิธีเร็วที่สุด: สั่งสอง skills ต่อกัน

แนบภาพ แล้วเปลี่ยนชื่อและ path ในข้อความนี้:

```text
ใช้ $reference-to-concept วิเคราะห์ภาพที่แนบเป็น primary reference

ชื่อชิ้นงาน: forest-lantern
การใช้งาน: โมเดลที่แก้ไขต่อได้ พร้อมวัสดุและ texture อย่างละเอียด
สิ่งที่ต้องรักษา: รูปทรง สัดส่วน รายละเอียดเด่นและการแบ่งวัสดุตามภาพ
ขนาดจริง: ไม่ทราบ ให้แยก working scale ออกจากขนาดจริง

แตก component สำคัญเป็นชิ้นส่วนย่อย พร้อมรายการรายละเอียดที่ต้องมี
ระบุสิ่งที่ต้องทำเป็น mesh และสิ่งที่ใช้ material/texture
สร้าง concept_sheet.png พร้อมมุมตรวจและภาพขยายที่อ่านโครงสร้างได้
แยก observed / inferred / proposed และบันทึกแบบที่เลือกใช้
ไม่ทำฉากเสริม แท่นโชว์ ชุดไฟ HDRI หรือ hero/cinematic render

เมื่อผ่าน QA ให้ใช้ $concept-to-model-prompt ต่อ
สร้าง prompt ไทยและอังกฤษครบ 7 หัวข้อ พร้อมเกณฑ์ตรวจราย feature
แพ็กเป็น forest-lantern_artifact.zip

เก็บชิ้นงานใต้:
C:\Users\User\Desktop\projects\modeling_output

เก็บ ZIP ที่:
C:\Users\User\Desktop\projects\modeling_output\packages
```

ได้โฟลเดอร์ `modeling_output/forest-lantern/` และ ZIP ใน `packages/` เมื่อขั้นตอนที่จำเป็นผ่านครบ

## แยกทำทีละขั้น

### 1. วิเคราะห์และสร้าง concept sheet

```text
ใช้ $reference-to-concept กับภาพที่แนบ
ชื่อ: ceramic-vase
ยึดภาพนี้เป็น primary reference รักษารูปทรง ปากภาชนะ ฐานและลวดลาย
สร้าง concept_sheet.png พร้อมภาพขยายของส่วนสำคัญ
ทำรายละเอียด mesh และแผน material/texture พร้อม feature ID และเกณฑ์ตรวจ
บันทึกใต้ C:\Users\User\Desktop\projects\modeling_output
ขั้นนี้ทำเฉพาะ concept กับข้อมูลส่งต่อ
```

หากแก้แบบ ให้สั่งอัปเดตภาพและข้อมูลร่วมกัน:

```text
แก้ปากภาชนะและฐานของ ceramic-vase ให้ตรง primary reference
อัปเดต concept sheet, analysis.json, details.md และ QA ให้ตรงกัน
บันทึกว่ารายละเอียดใดเป็นการตัดสินใจที่เลือกใช้แล้ว
```

### 2. เขียน prompt และแพ็ก

```text
ใช้ $concept-to-model-prompt กับโฟลเดอร์:
C:\Users\User\Desktop\projects\modeling_output\ceramic-vase

สร้าง prompt ไทยและอังกฤษที่มีข้อกำหนดตรงกัน
เน้น mesh รายชิ้น พร้อมวัสดุและ texture อย่างละเอียด
ทุก required feature ต้องมีคำสั่งสร้าง แหล่งแบบที่เลือก crop และเกณฑ์ตรวจภาพวางเทียบกัน
แพ็กไว้ที่ C:\Users\User\Desktop\projects\modeling_output\packages
```

## Prompt ใหม่มี 7 หัวข้อ

| หัวข้อ | เนื้อหา |
|---|---|
| 1. Geometry & Proportions | รูปทรง สัดส่วน หน้าตัด ความหนา ท่าทางและช่องว่าง |
| 2. Reference Fidelity & Design Decisions | สิ่งที่ต้องเหมือน หลักฐาน แบบที่เลือกใช้ และขอบเขตการลดรายละเอียด |
| 3. Components & Mesh Details | ชิ้นส่วนย่อย รอยต่อ ช่องเปิด ชั้นผิว และต้นแบบของชิ้นซ้ำ |
| 4. Topology & Assembly Quality | คุณภาพ mesh, normals, modifiers จุดยึดและข้อผิดพลาด |
| 5. Materials & Textures | วัสดุละเอียด UV/mapping, ลวดลาย รอยสึกและ texture resources |
| 6. Modeling Progression | ลำดับสร้าง จุดตรวจ checkpoint และการกลับไปแก้ |
| 7. Verification & Delivery | ภาพตรวจ ผลราย feature ไฟล์ .blend, texture และรายงาน |

ลำดับทำจริง: **blockout → โครงสร้าง/ต้นแบบชิ้นซ้ำ → รายละเอียด mesh → ตรวจและแก้ mesh → วัสดุ/texture → ตรวจส่งมอบ**

ชิ้นซ้ำที่ซับซ้อนต้องทำต้นแบบหนึ่งชุดให้ผ่านก่อนทำซ้ำ รายละเอียดที่มีผลต่อ silhouette หรือความลึกต้องเป็น geometry ตามแบบ ส่วนรอยผิวเล็กใช้ texture ได้ตามขนาดที่ต้องดู ไม่บังคับรูปแบบเดียวกับตัวละคร อาคาร หรือเครื่องจักรทุกงาน

## ความสมมาตรของโครงสร้างและขา

สำหรับขาหรือชิ้นส่วนที่ตั้งใจให้เป็นคู่เหมือนกัน ให้สร้างโครงสร้างฐานสมมาตรก่อนจัดท่า โดยต้อง:
- ระบุคู่ซ้าย–ขวา ระนาบ/แกนสมมาตร และขนาดที่ใช้ร่วมกัน เช่น ความยาวแต่ละท่อน หน้าตัด ความหนาเกราะและตำแหน่งข้อต่อ
- ใช้ต้นแบบเดียวแล้ว mirror/duplicate หรือใช้พารามิเตอร์ร่วม ห้ามขึ้นขาแต่ละข้างด้วยการกะสายตาแยกกัน
- วางจุดยึดคู่ให้สะท้อนกันรอบระนาบกลางลำตัว ตรวจจากมุมตรงและมุมบนในท่ากลางก่อนจัดท่า
- ตรวจค่าความต่างของขนาด จุดยึดและ pivot เทียบกับ tolerance ตามสเกลโมเดล พร้อมบันทึกผลผ่าน/ไม่ผ่าน
- ใช้ท่ายืนสมมาตรเมื่อไม่ได้กำหนดท่าต่างกัน หากต้องจัดท่าตามภาพ ให้หมุนข้อต่อโดยคงความยาวและรูปทรงฐาน ไม่ยืดขาแยกข้างเพื่อให้ตรง perspective หรือแตะพื้น
- แยกคู่ขาหน้ากับคู่ขาหลัง ไม่เหมาว่าขาทั้งสี่ต้องเหมือนกันทุกอย่าง และรักษาเครื่องมือหรือรายละเอียดที่ตั้งใจให้ต่างกัน

ความต่างจาก perspective หรือการบังกันไม่ใช่หลักฐานว่าขามีขนาดต่างกัน ส่วนที่อนุมานให้บันทึกเป็นการตัดสินใจออกแบบ ความสมมาตรแต่ละกลุ่มต้องเป็น required feature ในข้อมูลและ prompt; ถ้าไม่ผ่านต้องแก้ก่อนทำวัสดุละเอียดหรือประกาศงานเสร็จ

ตัวอย่างคำสั่งเสริม: “เน้นขาซ้าย–ขวาให้สมมาตรทั้งขนาด รูปทรงและจุดยึด ใช้ต้นแบบเดียว ตรวจท่ากลางก่อนจัดท่า และส่งผลเปรียบเทียบค่าความต่างด้วย”

## รายละเอียดที่ต้องมีและวิธีตรวจ

แต่ละ component มี feature ID พร้อม:
- ตำแหน่งใน reference และสถานะ observed/inferred/proposed
- รูปทรงหรือคุณสมบัติผิวที่ต้องสร้าง
- วิธีแทนด้วย geometry/material/texture/both
- required, must_preserve และขอบเขตที่ลดรายละเอียดได้
- มุมตรวจและเกณฑ์ผ่านที่มองเห็นได้

แบบที่เลือกใช้แล้วมี decision ID แยกจากความแน่นอนของหลักฐาน ส่วนที่อนุมานยังเป็นส่วนที่อนุมาน แม้เลือกใช้แล้วก็ตาม ต้องตรวจซ้าย–ขวาของภาพ ตัวแบบและแกนพิกัดให้ตรงกัน

ภาพ concept ที่ดูดีหรือจำนวนชิ้นส่วนครบยังไม่พอสำหรับผ่าน QA รายละเอียดสำคัญที่ขาดต้องแก้ก่อน ไม่ใช่เพียงบันทึกข้อจำกัดแล้วประกาศเสร็จ แยกผลตรวจ geometry/detail, topology/assembly และ material/texture ออกจากกัน

## แหล่งแบบของรายละเอียดและภาพเทียบ

แยกหลักฐานจากภาพกับแบบที่เลือกให้สร้างตาม: primary reference คุมเอกลักษณ์และสิ่งที่เห็นชัด ส่วนช่องขยายใน concept ที่เลือกแล้วเป็นแบบหลักของรายละเอียดที่ได้รับมอบหมายได้ แม้ภาพหลักจะไม่ชัด รายละเอียดนั้นยังมีสถานะ inferred/proposed แต่ไม่ใช่ข้ออ้างให้ข้ามการสร้าง

แต่ละ feature ต้องมี design_source ระบุแหล่งภาพ/ช่อง concept/decision พร้อมเหตุผล และ detail_spec ที่บอกสิ่งที่ต้องมี: ตำแหน่ง จำนวนหรือความไม่แน่นอน รูปหน้าตัด สัน ขอบ ชั้นซ้อน ร่องและความสัมพันธ์กับชิ้นข้างเคียงตามประเภทวัตถุ ไม่ใช้เพียงคำว่า “ทำให้ละเอียด” หรือรายการสิ่งที่ห้ามทำ

ค่าตัวเลขมีที่มา user/estimated/design_choice พร้อมหน่วย กรอบพิกัด จุดเริ่ม–จุดสิ้นสุดและ tolerance เช่น z=0 ที่กลางลำตัวเป็นพิกัดท้องถิ่น ไม่ใช่ z=0 ของพื้นโลก ช่วงกางขาต้องระบุคู่เท้า แกนและท่าที่ใช้วัด ไม่เติมจำนวนชิ้นหรือขนาดอย่างไร้ที่มา

skill แรกแนบ crop จากภาพต้นฉบับและช่อง concept ที่เลือกไว้ใน detail_crops/ พร้อม bbox, source ID, feature IDs และคำอธิบายใน JSON/details.md ใช้พิกเซลจากภาพจริง ไม่สร้างรายละเอียดเพิ่มด้วยการขยายภาพ แล้วอ้างว่าเป็นหลักฐานเดิม

## สองเฟสและรอบตรวจรายละเอียด

**Phase A — โมเดลและรายละเอียด:** สร้าง mesh ตรวจสมมาตร/จุดยึด/topology แล้วทำภาพ close-up วางเทียบ crop ข้างกันอย่างน้อยหนึ่งรอบ ครอบคลุม required geometry features ทุกข้อ ลิสต์จุดที่ขาดหรือผิด แก้และถ่ายเทียบใหม่จนผ่านก่อนทำวัสดุละเอียด หากผ่านตั้งแต่รอบแรก ไม่ต้องแก้เพียงเพื่อให้ครบจำนวนรอบ

**Phase B — วัสดุ/texture และส่งมอบ:** เข้าได้เมื่อ Phase A ผ่านแล้ว ทำวัสดุและ texture อย่างละเอียด เทียบภาพผิวกับ crop ที่เลือก หาก displacement หรือข้อผิดพลาดใหม่กระทบรูปทรง ให้กลับไปตรวจ Phase A ที่เกี่ยวข้องอีกครั้ง

ผลสร้างโมเดลต้องมีภาพ side-by-side ใน comparisons/ หรือโฟลเดอร์ที่ระบุ พร้อม crop/feature IDs และรายงานแต่ละรอบใน verification.md รายละเอียดทุกข้ออาจกระจายหลายมุมได้ แต่ต้องเห็นชัดอย่างน้อยหนึ่งภาพ หรือระบุ not_verified ไม่ใช้ภาพ silhouette รวมแทนการตรวจใกล้

ไม่เพิ่มเฟสจัดแสง ฉากหรือ beauty render การแยกสองเฟสใช้ใน prompt เดียวภายใต้ 7 หัวข้อเดิม

## ไฟล์ที่ได้จากสอง skills

```text
<name>/
  references/primary_reference.<original-extension>
  references/<supporting-images>
  detail_crops/<declared-primary-and-concept-crops>.png
  analysis.json
  analysis.md
  concept_sheet.png
  concept_sheet_prompt.md
  details.md
  concept_qa.md
  handoff.md
  model_prompt.th.md
  model_prompt.en.md
  build_spec.json
  usage.th.md
  usage.en.md
  prompt_qa.md

<name>_artifact.zip
  <name>/<files-above>
  <name>/manifest.json
```

`analysis.json` เก็บ component/features, material/texture plans และ decisions ส่วน `build_spec.json` มี 7 topics กับ `feature_plan` ซึ่งต้องครอบคลุม required features ทั้งหมด

Manifest ระบุรายการไฟล์ ขนาดและ SHA-256 ตัวแพ็กเลือกเฉพาะไฟล์ที่กำหนด references และ detail_crops ที่ประกาศ ไม่รวมไฟล์อื่นโดยอัตโนมัติ

## นำ ZIP ไปสร้างโมเดลจริง (`$model-prompt-to-blender`)

ต้องมี:
- Blender (ทดสอบกับ 5.2) พร้อม add-on MCP for Blender ที่เชื่อมกับ agent
- Python 3.10+ ที่มี Pillow และ numpy สำหรับเครื่องมือภาพ
- GPU (ถ้ามี): skill จะเรนเดอร์ Cycles ด้วย GPU อัตโนมัติ (OptiX > CUDA > HIP > oneAPI > Metal ใช้เฉพาะการ์ดแยก) ถ้าไม่มีจะใช้ CPU แทน การเรนเดอร์ OptiX ครั้งแรกในเครื่องจะโหลด kernel ราว 45 วินาที ครั้งต่อไปเร็วขึ้น

ขั้นตอน:
1. แตก ZIP ให้ agent เข้าถึงทั้งโฟลเดอร์
2. สั่ง skill พร้อม path และ output directory

```text
ใช้ $model-prompt-to-blender กับโฟลเดอร์:
C:\Users\User\Desktop\projects\modeling_output\ceramic-vase
อ่าน model_prompt.en.md, build_spec.json, analysis.json, detail_crops และ concept_sheet.png
สร้างโมเดลใน Blender ตาม gate ของ prompt พร้อมวัสดุและ texture อย่างละเอียด
ทำตารางรายละเอียดก่อนขึ้นโมเดล และเทียบ close-up ราย feature ก่อนเข้าขั้นวัสดุ
เก็บ .blend ทุก checkpoint, ภาพตรวจ, ภาพเทียบ และ verification.md ใน model_output
ไม่เพิ่มฉากเสริม ชุดไฟ HDRI หรือ hero/cinematic render
```

skill จะทำสิ่งต่อไปนี้
- **ตรวจ package ก่อนเริ่ม** ได้แก่ ซ้าย-ขวาและแกน, เจตนาสมมาตร, ส่วนที่ต้องอยู่กลาง และช่วงตัวเลขที่ขัดกับ concept แล้วบันทึกการตัดสินใจ
- **สร้างใน scene แยก** (`<Name>_Scene`) ไม่แตะ scene เดิมของผู้ใช้
- **ใช้สคริปต์ procedural ที่รันซ้ำได้** ร่วมกับไลบรารีใน `scripts/` (`bl_build`, `bl_detail`, `bl_materials`, `bl_views`, `bl_check`, `bl_symmetry`, `img_tools`)
- **รอเรนเดอร์นานด้วย marker file:** งานที่นานเกินราว 120 วินาทีจะรอแบบ background เพราะ MCP timeout ไม่ได้แปลว่างานล้ม
- **ยืนยันผลจริง:** เปิดไฟล์ .blend ซ้ำใน Blender แยกโปรเซส และรายงานผลราย feature

### แก้รายละเอียดหลังส่งงาน (`$blender-detail-repair`)

```text
ใช้ $blender-detail-repair กับโมเดล ceramic-vase
ขาเรียบเกินไปเมื่อเทียบ reference — crop reference/concept ส่วนขา แล้วเรนเดอร์มุมเดียวกัน
เขียน gap list แล้วแก้ใน build script ตรวจ topology/symmetry ใหม่ เรนเดอร์ทั้งชุด และเพิ่ม Revision ใน verification.md
```

### ตรวจและเรนเดอร์ใหม่ (`$blender-model-verify`)

```text
ใช้ $blender-model-verify กับ C:\Users\User\Desktop\projects\modeling_output\ceramic-vase\model_output
ตรวจ topology และ symmetry, เรนเดอร์ภาพตรวจทั้งหมดใหม่, เปิด .blend ซ้ำแบบ background
ตรวจขนาดภาพ และอัปเดต verification.md
```

ผลขั้นนี้ควรมีไฟล์ .blend ที่แก้ไขได้ checkpoint ตามความจำเป็น texture ที่แพ็กไว้ในไฟล์หรือแนบ path ที่ใช้ได้ ภาพตรวจและรายงานราย feature งานที่ยังมี required feature ไม่ผ่านต้องระบุ partial/needs_revision

## แพ็ก ZIP ด้วยตัวเอง

```powershell
python "C:\Users\User\Desktop\projects\share_skill\modeling\concept-to-model-prompt\scripts\package_artifact.py" `
  --project "C:\Users\User\Desktop\projects\modeling_output\ceramic-vase" `
  --output-dir "C:\Users\User\Desktop\projects\modeling_output\packages"
```

ตัวแพ็กตรวจ schema, scope, feature coverage, แหล่งแบบ/crop/แผนเทียบภาพและเกณฑ์สองเฟส, การอ้าง feature ใน prompt สองภาษา, QA status, โครงสร้าง PNG และ ZIP/hash ไม่สามารถรับรองความเหมือนของภาพหรือความเท่าเทียมทางความหมายของสองภาษาแทนผู้ตรวจได้

หาก ZIP ชื่อเดิมมีอยู่แล้ว สคริปต์จะหยุด ให้เลือก output directory ใหม่สำหรับเวอร์ชันถัดไป

## งานจากเวอร์ชันเดิม

เวอร์ชันนี้ใช้ `schema_version: 3` สำหรับ analysis/build_spec/manifest พร้อมหัวข้อใหม่ ตัวแพ็กจะปฏิเสธ schema 1/2 โดยแจ้งให้ migrate

สำหรับงานเก่า ให้สร้างโฟลเดอร์เวอร์ชันใหม่ ตรวจ reference อีกครั้ง เลือกแหล่งแบบราย feature เติม detail inventory/measurement/decision/material records แนบ crop และแก้ orientation และสร้าง prompt/spec/usage ใหม่ จากนั้นตรวจ QA ใหม่ก่อนแพ็ก **ห้ามเปลี่ยนเฉพาะเลข schema หรือคงสถานะ approved จาก brief เก่า**

การอัปเดต skill ไม่แก้ prompt, ZIP หรือโมเดลที่สร้างไว้แล้วโดยอัตโนมัติ หากงานเก่ามีสคริปต์เช่น author_model_prompts.py ต้องตรวจข้อความที่ฝังไว้ก่อนใช้ซ้ำ มิฉะนั้นอาจสร้าง prompt รุ่นเก่ากลับมา

## เมื่อทำต่อไม่ได้

| อาการ | วิธีดำเนินการ |
|---|---|
| ไม่มี primary reference | แนบภาพหรือระบุ path ที่เข้าถึงได้ |
| ภาพหลายใบขัดกัน | ระบุ primary แล้วบันทึกการตัดสินใจราย feature |
| เครื่องมือสร้างภาพใช้ไม่ได้ | เก็บ analysis และ generation brief แล้วรายงาน blocked_image_generation |
| Concept ขาดรายละเอียดสำคัญ | แก้ภาพหรือทำข้อสรุปจากหลักฐานให้ชัดก่อนอนุมัติ |
| Feature plan ไม่ครบ | เติมคำสั่งสร้างและเกณฑ์ตรวจของรายการที่หาย |
| วัสดุ/texture ยังไม่มีแผน | ระบุโซน คุณสมบัติผิว mapping และเกณฑ์ตรวจ |
| แพ็กเกจเก่าไม่ผ่าน | ทำ migration ตามขั้นตอนข้างต้น |
| ไม่มีภาพตรวจจาก Blender | ระบุ not_verified/partial ไม่อ้างว่าผ่านจากจำนวน object |
| MCP แจ้ง timeout ระหว่างเรนเดอร์ | Blender ยังทำงานต่อ ให้รอ marker file ห้ามสั่งเรนเดอร์ซ้ำ |
| รายละเอียดเรียบกว่า reference | ใช้ `$blender-detail-repair` ทำ gap list จากภาพ close-up เทียบ crop |
| แผงเกราะไม่แยกตามรอยต่อ | ตรวจว่ารอยต่อปิดเป็นวงและไม่มีช่องว่างระหว่าง cutter ดู `model-prompt-to-blender/references/pitfalls.md` |

## Source และชุดติดตั้ง

Source สำหรับแชร์:

```text
C:\Users\User\Desktop\projects\share_skill\modeling\
  README.md
  reference-to-concept/
  concept-to-model-prompt/
  model-prompt-to-blender/     (SKILL.md, references/, assets/, scripts/, examples/orange-orb-walker/)
  blender-detail-repair/       (ใช้ scripts/ และ references/ ของ model-prompt-to-blender)
  blender-model-verify/        (ใช้ scripts/ และ assets/ ของ model-prompt-to-blender)
  WORKFLOW.md                  คู่มือใช้งานทั้ง pipeline
  setup/                       install_skills.py, install.ps1, install.sh, SETUP.md
```

ติดตั้งและซิงก์ด้วยตัวติดตั้ง ไม่ต้องคัดลอกเอง รายละเอียดอยู่ใน [setup/SETUP.md](setup/SETUP.md)
- **skill ครบในตัว:** skill ฝั่ง Blender จะได้สำเนา `scripts/`, `references/` และ `assets/` ที่ใช้ร่วมกันไปด้วย
- **สำรองของเดิมก่อนทับ:** ย้ายไปไว้ที่ `~/.skill_backups/`

```text
Claude Code:          ~/.claude/skills/<skill>          (.\setup\install.ps1 claude-code)
Codex / ChatGPT app:  ~/.agents/skills/<skill>          (.\setup\install.ps1 codex | chatgpt-desktop; Codex เวอร์ชันเก่าเพิ่ม --codex-legacy -> ~/.codex/skills)
Claude app / web:     setup/dist/claude-app/<skill>.zip (.\setup\install.ps1 claude-app แล้วอัปโหลดที่ Customize > Skills)
ChatGPT web:          setup/dist/chatgpt/<skill>.zip    (.\setup\install.ps1 chatgpt-web)
Blender library:      <Blender user>/scripts/modules    (.\setup\install.ps1 blender  ->  import bl_build ได้ทันที)
```

แก้ source แล้วให้รันคำสั่งติดตั้งเดิมซ้ำเพื่อซิงก์ เก็บไฟล์ชิ้นงานแยกจากโฟลเดอร์ skill

ทดสอบไลบรารี Blender ด้วยคำสั่งด้านล่าง รันใน Blender แยกโปรเซสจึงไม่แตะ session ที่เปิดอยู่ ต้องได้ `SMOKE_OK` และ `NO_SHELL_OK`

```powershell
.\setup\install.ps1 smoke
```

ตรวจตัวแพ็กได้ด้วย:

```powershell
python -B -m unittest discover -s "C:\Users\User\Desktop\projects\share_skill\modeling\concept-to-model-prompt\scripts" -p "test_*.py" -v
```

