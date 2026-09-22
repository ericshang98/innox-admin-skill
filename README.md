# 深科创学院行政办理指南

为深圳科创学院团队准备采购、验收、经费预支、核销与报销材料的 Agent Skill。先读取长期档案，再按本次事项判断流程、填写 Word 草稿、整理系统填写内容和附件。已确认的团队信息不反复问，每笔采购独立记录。

**当前为规则审核稿，未获学院现行制度确认，未接通学院 API 或自动审批提交。** 三份 Word 为用户提供的原始参考模板，包含样例，使用时需清除。项目不是学院官方发布的制度。

## 审核指南

下载仓库后，用浏览器直接打开 [行政办理指南](docs/rules-review.html)。静态 HTML 无脚本、无问卷，不需要本地服务器。旧链接 `docs/review-template.html` 保留同样内容。

指南依次说明：长期档案与本次事项、流程判断、采购金额、资金路径、验收、字段填写、材料交付、完整示例和例外处理。内部证据在规则库中维护，不将条款追溯堆进办理正文。

## 使用 Skill

把下面这段话复制给你正在使用的 Agent，再附上已有订单、合同或发票：

> 请读取并使用这个 Skill，以及其中的规则和 Word 模板，帮我准备深圳科创学院的行政办理材料：
> https://github.com/ericshang98/innox-admin-skill
>
> 我要办理的事是：[写你要买什么或报销什么]。请根据我提供的材料准备表格和填写内容，缺少必要信息时直接问我。

以后办理新事项，直接说明这次要办什么，并提供本次材料。已保存的团队信息会继续沿用；团队或阶段有变化时告诉 Agent 即可。

Agent 应读取完整的 `skills/innox-invoice/`，包括 `SKILL.md`、`references/`、`scripts/` 和 `assets/`。若所用 Agent 无法读取 GitHub，可下载仓库后把完整 Skill 文件夹交给它。实际文件处理和长期保存能力取决于运行环境；本项目不会自行取得学院系统权限。

Agent 开始办理时先读取 `references/memory.md`。本地档案默认保存在 `~/.local/share/innox-admin/`，也可通过 `INNOX_ADMIN_DATA_DIR` 指定私有目录。档案与模板获取脚本只用 Python 标准库，验收单填写工具使用文档依赖：

- `records.py`：持久保存团队、成员与事项，支持历史版本和写入冲突检查。阶段变更保留生效日；既有事项保留当时的资料快照。
- `prepare_template.py`：校验并复制原始模板；随包文件缺失时从 GitHub 获取。
- `fill_acceptance.py`：根据 Agent 提取的本次事实填写三类验收单，计算明细金额、插入照片，输出 Word 草稿及缺件记录。需要 `scripts/requirements.txt` 中的文档依赖。

本地档案不是团队云服务。更换设备需迁移私有目录；未提供持久存储的运行环境不能承诺跨会话记忆。无需每次确认长期资料，只有缺失、变更、冲突或跨阶段事项才补问相关信息。

## 让 Agent 帮你做验收单

把已有材料交给 Agent，直接说：

> 请用这个 Skill 帮我做本次采购的验收单。根据订单、发票和交付材料选用适合的模板，填写明细、核对金额、放入收货照片，给我可编辑的 Word 草稿，并说明还缺什么、哪里需要验收和签字。

你不用找空表或自己排版。三份原始模板已随 Skill 分发，Agent 根据采购途径和交付类型判断使用哪份。货物提供真实收货照片；服务提供合同、服务期间和交付证据。材料不齐可以先做已有部分；验收结论、评分、签字盖章留给对应人员。详细执行方式见 [验收单生成流程](skills/innox-invoice/references/acceptance-generation.md)。

## 原始 Word 模板

| 模板 | 内容 |
| --- | --- |
| [团队自采](skills/innox-invoice/assets/templates/self-purchase.docx) | 明细、验收照片、经办人与辅导老师签字 |
| [货物类](skills/innox-invoice/assets/templates/goods.docx) | 货物明细、验收检查及学院意见 |
| [服务类](skills/innox-invoice/assets/templates/service.docx) | 服务验收单与采购项目履约评价表 |

原文件名、版本、下载地址和哈希见 [模板清单](skills/innox-invoice/assets/templates/manifest.json)。文件保持原样供复用，样例项目、姓名、部门与金额均不能作为用户交易事实。每次复制到本次事项的私有目录后填写，不覆盖模板原件。

## 维护

- `skills/innox-invoice/SKILL.md`：Agent 的办理入口。
- `references/decision-guide.json`：Agent 与 HTML 共用的流程内容。
- `references/rules.json`：培训与模板提取的规则候选及证据状态。
- `references/wecom.md`：独立保留的技术调研，只有需要系统接入时阅读。
- `scripts/build_review.py`：重新生成两份 HTML；运行 `python3 scripts/build_review.py`。

公开仓库保存 Skill、规则摘要及用户要求分发的三份原始模板。团队档案、成员资料、实际票据、填好的表格、签名、录音及完整转写均保存在私有目录。

原创代码及指南采用 MIT 许可证。学院原始模板不纳入该许可证，相关权利归原权利人；本仓库提供参考副本，不表示学院对规则或项目的官方背书。
