# API Integrations Design

各平台 API 集成设计文档。每个新平台集成前必须在此文档中完成设计。

---

## Integration Template

新增平台时，复制以下模板填写：

```markdown
### [平台名称]

**Task Type**: API-Driven / Prompt-Driven
**官方文档**: [链接或 N/A]
**逆向来源**: [抓包/开放API/第三方库]

**认证方式**:
- 类型: Cookie / Token / OAuth
- 存储: 环境变量 `DAILYHUB_{PLATFORM}_XXX`
- 有效期: [说明]

**核心接口**:
| 功能 | Method | Endpoint | 备注 |
|------|--------|----------|------|
| 签到 | POST | /xxx | |

**请求示例**:
\`\`\`
Headers: { ... }
Body: { ... }
\`\`\`

**响应示例**:
\`\`\`json
{ "code": 0, "msg": "success" }
\`\`\`

**限流说明**: [频率限制]
**注意事项**: [特殊处理]
```

---

## Integrated Platforms

### 小桔充电 (Xiaoju Charging)

**Task Type**: API-Driven  
**官方文档**: N/A（内部接口）  
**逆向来源**: App 抓包 + H5 bundle 反查

**认证方式**:
- 类型: Ticket + Token + TokenId（Header + Body）
- 存储: 环境变量（`DAILYHUB_XIAOJU_*`）
- 有效期: 非长期有效，过期后需调用方更新凭证

**核心接口**:
| 功能 | Method | Endpoint | 备注 |
|------|--------|----------|------|
| 查询签到状态 | POST | `/am/marketing/api/member/charge/activity/sign/main` | 返回当轮签到状态、`excitationId` |
| 执行签到 | POST | `/am/marketing/api/member/charge/activity/sign/doSign` | 需携带 `excitationId` |
| 查询签到记录 | POST | `/excitation/api/excitation/signRecord` | 近30天记录，校验页面一致性 |

Base URL（online）:
- `https://energy.xiaojukeji.com`

**请求示例**:
```json
Headers: {
  "content-type": "application/json; charset=utf-8",
  "ticket": "<ticket>",
  "user-agent": "okhttp/3.14.9"
}
Body(sign/main): {
  "ticket": "<ticket>",
  "token": "<token>",
  "tokenId": "<token_id>",
  "appId": 121358,
  "amChannel": 1323124385,
  "source": "1323124385",
  "ttid": "driver",
  "bizLine": 250,
  "cityId": 5
}
```

**响应示例**:
```json
{
  "success": true,
  "status": 10000,
  "code": "SERVICE_RUN_SUCCESS",
  "data": {
    "signInfo": [
      {
        "excitationId": "144115195993789098",
        "signTaskDTO": {
          "signRecordDTOList": [
            {"signDate": "2026-03-09", "index": 0}
          ]
        }
      }
    ]
  }
}
```

**限流说明**: 未观察到公开限频策略，建议每日触发 1 次，失败重试最多 3 次。  
**注意事项**:
- `sign/main` 返回的签到记录是“当轮视角”，与记录页历史接口不同
- `signRecord` 在 `energy` 域名可用，`gw.am` 直调可能返回 `501`
- 对于“已签到”状态必须视为成功（幂等）

---

_Last updated: 2026-03-09_
