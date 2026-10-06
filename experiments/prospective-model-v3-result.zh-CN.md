# 前瞻真实模型研究 v3 结果

> [English](prospective-model-v3-result.md) | 简体中文

## 结果

`prospective-offboarding-v3` **没有**产生可接受的 comparative frontier 结果。

v3 尝试通过 Responses Structured Outputs 的 strict JSON Schema 消除 v2 的 free-form JSON failure mode。请求路径接受了 `text.format=json_schema` 字段，但本地 gateway/upstream route 实际并没有执行该 schema 约束。

因此该 run 未通过预注册的 model-interface qualification。

## Run 身份

AIOS workflow run：

~~~text
37399859506
~~~

固定证据：

~~~text
workload: prospective-offboarding-v3
prompt profile: evidence-neutral-v3-structured
model: gpt-6-luna
requested model interface: json_schema
BAA preregistration: 9c5fec4376b7e3c3f51d7c042bf074eff3ec0e21
AIOS workflow head: 0d6405f3cee49834ef54523be9115d5ef24e6cef
gateway: 496ec69a5b1f578ae837498037f4badf6e4c2dbc
~~~

workload fingerprint 与 gateway check 都通过。study 完整执行并上传 evidence，但 qualification 失败。

## 证据

artifact 报告：

~~~text
physical calls: 108
calls with errors: 107
transport errors: 0
schema errors: 107
model/refusal errors: 0
input tokens: 50886
output tokens: 23800
~~~

这些不是 transport failure。

最常见的 initial output 使用 `type`，而不是 strict schema 要求的 `kind`，例如：

~~~json
{
  "actions": [
    {
      "type": "execute",
      "obligation_id": "obl:identity",
      "subject_ref": "employee:alpha",
      "target_system": "iam",
      "operation": "identity.disable",
      "authority_epoch": 4
    }
  ]
}
~~~

其他输出还改变顶层结构，或加入 strict schema 中不存在的 `reason`、`proposal`、`proposals`、`subject`、`target` 等字段。

这与声明的 strict JSON Schema 不相容。

## 解释

该 run 最多建立：

> 当前本地 `gpt-6-luna` Responses route 会接受包含 `text.format=json_schema` 的请求，但这个字段在该 deployment path 上不是可靠的执行约束边界。

它**不能**说明底层模型一般性地不支持 Structured Outputs。

它也**不能**产生 BAA delegation-frontier 结论。

artifact 中机械生成的 0/12 regime summary 只是 proposal parse failure 的产物，没有 comparative meaning。

## 为什么不能放宽 parser

如果根据已观察输出，让 BAA parser 事后接受 `type`、`proposal`、`subject` 等变体，就会通过移动接口边界让实验“成功”。

这会：

- 违反冻结的 v3 qualification rule；
- 把 schema drift 隐藏成 parser policy；
- 让后续比较依赖不断扩张的 compatibility parser，而不是固定 proposal contract。

因此 v3 保留为 qualification failure。

## 下一边界

在冻结下一轮 comparative study 前，必须先证明当前 deployment path 上存在一个**真正机器强制**的 proposal interface。

下一步先做独立 capability probe：使用 strict function parameters 强制 Responses function call。

只有当 route 返回真实 `function_call`，且 arguments 符合声明 schema 时，才把该接口用于新的 prospective study version。

## 后续 capability probe

AIOS workflow run `37401308580` 随后完成了该独立 probe。

固定环境：

~~~text
model: gpt-6-luna
gateway: 496ec69a5b1f578ae837498037f4badf6e4c2dbc
function: submit_baa_proposal
tool_choice: forced function
strict: true
~~~

结果：

- probe step 成功；
- 唯一 output type 为 `function_call`；
- arguments 精确包含 `kind`、`obligation_id`、`subject_ref`、`target_system`、`operation`、`authority_epoch`；
- 没有额外字段；
- `authority_epoch` 保持 integer；
- probe 不执行任何现实动作。

因此该 deployment path 已对 forced strict function calling 给出正向 capability evidence。下一轮 prospective study 可以在新版本中使用这一接口。
