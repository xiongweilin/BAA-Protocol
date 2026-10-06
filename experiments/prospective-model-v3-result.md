# Prospective Real-Model Study v3 Result

> English | [简体中文](prospective-model-v3-result.zh-CN.md)

## Outcome

`prospective-offboarding-v3` did **not** produce an accepted comparative frontier result.

v3 attempted to remove v2's free-form JSON failure mode by using Responses Structured Outputs with a strict JSON Schema. The request path accepted the `text.format=json_schema` field, but the local gateway/upstream route did not actually enforce that schema.

The run therefore failed its preregistered model-interface qualification.

## Run identity

AIOS workflow run:

~~~text
37399859506
~~~

Pinned evidence:

~~~text
workload: prospective-offboarding-v3
prompt profile: evidence-neutral-v3-structured
model: gpt-6-luna
requested model interface: json_schema
BAA preregistration: 9c5fec4376b7e3c3f51d7c042bf074eff3ec0e21
AIOS workflow head: 0d6405f3cee49834ef54523be9115d5ef24e6cef
gateway: 496ec69a5b1f578ae837498037f4badf6e4c2dbc
~~~

The workload fingerprint and gateway checks passed. The study executed and uploaded complete evidence, but qualification failed.

## Evidence

The artifact reported:

~~~text
physical calls: 108
calls with errors: 107
transport errors: 0
schema errors: 107
model/refusal errors: 0
input tokens: 50886
output tokens: 23800
~~~

The failures were not transport failures.

The dominant initial-output pattern used `type` instead of the schema-required `kind`, for example:

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

Other outputs changed the top-level shape or introduced fields not present in the strict schema, including `reason`, `proposal`, `proposals`, `subject`, and `target`.

This behavior is incompatible with the declared strict JSON Schema.

## Interpretation

The run establishes only:

> The current local `gpt-6-luna` Responses route accepts a request containing `text.format=json_schema`, but that field is not a reliable enforcement boundary for this deployment path.

It does **not** establish that the underlying model lacks Structured Outputs generally.

It does **not** establish a BAA delegation-frontier result.

The mechanically emitted 0/12 regime summaries are artifacts of proposal parse failure and have no comparative meaning.

## Why parser relaxation is rejected

Changing the BAA parser to accept `type`, `proposal`, `subject`, or other observed variants would make the experiment appear to succeed by moving the interface boundary after seeing model outputs.

That would:

- violate the frozen v3 qualification rule;
- turn schema drift into hidden parser policy;
- make later comparison depend on an expanding compatibility parser rather than a fixed proposal contract.

Therefore v3 remains a qualification failure.

## Next boundary

Before freezing another comparative study, the deployment path must first demonstrate a proposal interface that is actually machine-enforced.

A separate capability probe should test a forced Responses function call with strict function parameters.

Only if the route returns a real `function_call` whose arguments conform to the declared schema should that interface be used in a new prospective study version.

## Follow-up capability probe

AIOS workflow run `37401308580` subsequently executed that probe independently of the comparative study.

Pinned environment:

~~~text
model: gpt-6-luna
gateway: 496ec69a5b1f578ae837498037f4badf6e4c2dbc
function: submit_baa_proposal
tool_choice: forced function
strict: true
~~~

Observed result:

- the probe step succeeded;
- the only output type was `function_call`;
- arguments contained exactly `kind`, `obligation_id`, `subject_ref`, `target_system`, `operation`, and `authority_epoch`;
- no additional fields were present;
- `authority_epoch` remained an integer;
- the probe executed no real-world action.

This provides positive capability evidence that the current deployment path supports forced strict function calling. A new prospective study version may therefore use that interface.
