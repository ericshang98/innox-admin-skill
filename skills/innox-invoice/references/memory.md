# 团队档案与事项记录

每次开始先读档，再提问。已确认且未出现变化迹象的长期信息直接沿用，不要求用户每笔重复确认。档案用于记忆事实，不代替学院规则。

## 保存位置

默认使用 `~/.local/share/innox-admin/`；可通过 `INNOX_ADMIN_DATA_DIR` 指定另一个私有目录。独立于 Skill 安装目录，更新或重装 Skill 不覆盖档案。使用 `scripts/records.py` 读写，成功回读后才称“已记住”。没有可持久化文件系统时说明只能沿用当前会话，不承诺下次记得。

```text
teams/<team-id>/profile.json                 团队长期信息及历史版本
teams/<team-id>/members/<member-id>.json      当前成员的个人资料
teams/<team-id>/cases/<case-id>.json          每笔事项及历史版本
teams/<team-id>/materials/<case-id>/          本次原附件、草稿和待签署表
```

`team-id`、`member-id`、`case-id` 由 Agent 生成稳定的英文／数字／短横线标识，无需用户填写。先用 `list` 查已有档案。能由当前任务明确匹配时直接读取；多团队／多成员且无法判断当前归属时，只问这一次属于谁，不能使用目录中第一个成员。用户更正、切换团队或阶段变更时更新相应档案，不影响其他团队。

## 长期信息

团队 `data` 推荐包含：

- `team_name`、`project_name`：经用户确认的团队与项目名称。
- `phase_history`：阶段记录数组，每项为 `phase`（预探索／探索）、`effective_from`（YYYY-MM-DD 或未知时 null）、`source`、`confirmed_at`。转阶段时追加，不覆盖旧阶段。若生效日未知，普通当前业务可使用已确认当前阶段，跨阶段费用必须补问日期。
- `funding_sources`：已确认的经费项目、标识及适用期间；不得把可选列表中出现过的经费视为本团队拥有。
- `contacts`：业务需要的经办人、导师等角色信息，不从他人记录套用。
- `invoice_identity`：学院已确认的抬头、税号及依据；未确认留空，不能凭学校名称猜税号。

成员 `data` 推荐包含 `name`、`department`、`role`、已核实的系统身份及必要的收款资料。团队共享事实与成员个人收款信息分开保存；另一成员办理时不能继承他人的银行卡。只存办理所需信息，不保存登录令牌、密码或企业 Secret。

事实注明来源和确认日期。只在用户报告变化、材料与档案冲突、费用跨阶段或来源明确失效时，核对相关字段，不对整份档案重新盘问。没有变更迹象时不定期要求用户重复确认。首次建档时简要说明保存位置，按本 Skill 的长期记录用途保存，不逐字段重复询问；用户要求不保存某项信息时遵从其选择。

## 每笔事项

新事项 `data` 包含 `member_id`、`title`、`team_profile_revision`、`team_snapshot`、`member_profile_revision`、`member_snapshot`、`facts`、`status`、`materials`、`outputs`、`missing`。快照仅包含本次实际用到的信息；归属阶段依据费用日期与阶段历史判断，不能机械使用“当前阶段”。

`facts` 记录本次购买内容、真实用途、供应商、数量单价、合同／订单总额、币种、本次付款额、已付款额、资金来源、订单／付款／费用日期、交付进度和相关单号。金额用十进制字符串。未知留空；不能把上笔供应商、金额、用途、验收结果自动继承。

`materials` 记录真实文件路径和缺件；`outputs` 记录已生成文件、模板 ID／哈希、是否待签署；`status` 区分准备中、待签署、待提交、审批中、退回、待核实、完成等实际状态，不能因已生成文档就记作审批完成。

更新团队资料不批量改写既有事项快照。旧事项确需更正时，记录原因和前后版本。用户继续办理时加载原 case 及附件，不新建重复事项。新建前用原单号、订单号和用户描述匹配；匹配不唯一时只问必要事实。

## 读写方式

在 Skill 目录运行（路径和 ID 为示例，由 Agent 替换）：

```bash
python3 scripts/records.py list
python3 scripts/records.py get --team team-a
python3 scripts/records.py list --team team-a
python3 scripts/records.py get --team team-a --member member-a
python3 scripts/records.py get --team team-a --case purchase-001
python3 scripts/records.py put --team team-a --input /private/path/team.json --expected-revision 0
python3 scripts/records.py put --team team-a --case purchase-001 --input /private/path/case.json --expected-revision 0
```

`--input` 为完整 `data` JSON 对象，不能是只含变化字段的片段；更新时先读当前版本，合并用户更正，再传当前 `revision`。首次创建传 0。写入保留旧版历史并回读；版本冲突时重新读取合并，不强行覆盖。输入文件和输出材料也放在私有目录。

用户要求查看、更正、清除记忆时按明确范围处理。清除时同时处理对应历史版本；不要以“历史不可删除”为由保留用户要求删除的数据。此实现是单设备本地档案，不是团队云同步；另一台设备须由用户迁移私有目录，不借 GitHub 同步业务数据。
