# Employee Offboarding Domain

## 1. Domain

This is the first concrete BAA-Protocol task domain.

[
D = 	exttt{employee-offboarding}
]

The domain is derived from the Administrative offboarding path in AIOS, which already separates governed facts, policy evaluation, authority, approval, execution authorization, external effects, independent read-back, reconciliation, completion, and responsibility discharge.

This repository does not claim to implement or certify AIOS. The AIOS documents and code are used as the source domain model for this BAA instance.

## 2. Reality-facing operations in scope

The initial external effect set is deliberately narrow:

- HRIS employee deactivation;
- IAM identity disablement;
- IAM session revocation.

Their expected reality-side postconditions are:

```text
hris.employee.deactivate:
  active == false

iam.identity.disable:
  enabled == false

iam.sessions.revoke:
  active_sessions == 0
```

Administrative-domain obligations such as identity-binding expiry, role-assignment expiry, role transfer, delegation expiry, and principal deactivation are relevant to completion, but are not represented as remote-provider effects in this first BAA executable model.

## 3. Structural inputs

A proposal for an external offboarding effect must bind at least:

```text
case_id
subject_ref
authority_epoch
governance_basis_id
obligation_id
target_system
operation
expected_postcondition
effective_at
capability_expiry
state_version
request_identity
```

The proposal is only eligible when:

- the case kind is employee-offboarding;
- the effect belongs to the current immutable obligation set;
- the authority epoch and governance basis are current;
- the operation is exactly one of the obligation's allowed operations;
- the target subject matches the obligation;
- the effective time has been reached;
- the verification path for the relevant target system is available or the deployment contract explicitly allows hold;
- the current information state remains inside the declared viable region.

## 4. Hard kernel property (I_K)

For covered interfaces, the first prototype attempts to enforce:

1. no external offboarding effect before the authoritative effective time;
2. no execution under a stale authority epoch or stale state version;
3. no execution for a subject, target system, or operation not bound to the admitted obligation;
4. no covered effect without a narrow capability;
5. no capability reuse after the proposal enters pending or settled state;
6. no automatic replay when the prior effect may have happened but confirmation is missing;
7. unresolved effects remain charged or force safe termination according to the deployment contract;
8. admitted actions cannot mutate the protected kernel, capability authority, VSAR, or independent observation sources.

These are interface / protocol properties. They are not, by themselves, claims that an employee was correctly selected for termination or that the underlying HR policy is normatively justified.

## 5. Real-world property (I_D^*)

The initial domain bridge targets only these bounded claims:

### Effect-scope property

Every covered reality-facing offboarding effect is attributable to a current, exact-scope obligation for the same case, subject, authority epoch, target system, and operation.

### Timing property

No covered deactivation / disablement / session-revocation effect is intentionally dispatched before the authoritative effective time.

### Verified-effect property

An external obligation is not treated as fulfilled merely because execution returned success. Fulfillment requires a current independent observation satisfying its frozen postcondition.

### Unknown-result property

If an execution result is ambiguous or verification is unavailable, the obligation remains unresolved and the protocol does not infer no effect or obtain implicit replay permission.

### Completion property

For the BAA experiment, a case is counted as externally complete only when all required external postconditions in scope have been independently verified. Administrative-domain obligations and responsibility discharge remain additional completion requirements outside this first executable kernel.

## 6. Bridge assumptions (Omega_{mathrm{bridge}})

The implication from (I_K) to the real-world claims above depends on:

- the HRIS subject identifier identifies the intended employee;
- the IAM subject identifier is correctly bound to the intended principal;
- the authoritative effective time source is current;
- the obligation set was produced from the intended policy and authority process;
- the executor is the only path available to the agent for the covered provider operations;
- independent read-back credentials / endpoints are not writable through admitted agent capabilities;
- HRIS read-back field `active` reflects employment activation state for the covered deployment;
- IAM read-back field `enabled` reflects login identity enablement for the covered deployment;
- IAM session read-back reports the active sessions relevant to the policy;
- provider-side request identity prevents ambiguous rebinding of a request to another subject or operation;
- relevant clocks and state-version comparisons are within the stated timing assumptions.

These assumptions are explicit. If any is not justified, the corresponding real-world guarantee must be weakened or withdrawn.

## 7. Information state (q_t)

The offboarding kernel operates over an information state containing at least:

- current case / authority epoch;
- current governance-basis qualification status;
- effective time and current clock interval;
- immutable obligation set identity;
- transfer / internal obligation blockers relevant to completion;
- admitted capabilities;
- reserved effects;
- pending / outcome-unknown effects;
- verified outcomes;
- observation freshness / availability;
- protected-source status;
- terminal pending policy.

The kernel does not assume access to the true external state.

## 8. Compatible-state treatment

For each attempted external effect, the information state preserves:

```text
definitely_not_effected
possibly_effected
verified_effected
```

An outcome-unknown provider result enters `possibly_effected`.

Observation unavailable / stale / unknown does not collapse `possibly_effected` to `definitely_not_effected`.

## 9. Viable region (mathcal W_Omega)

The first prototype uses a conservative viable region rather than a maximal one.

A state is eligible for another external offboarding dispatch only if:

- the next operation has a current exact-scope obligation and capability;
- no previous effect for that obligation is unresolved;
- the authority epoch and state version remain current;
- the effective time has been reached;
- the protected observation path has not been invalidated;
- the deployment can still refuse all future covered effects without violating a claimed hard safety property.

This region supports safety by stopping further effects. It does **not** guarantee eventual completion.

## 10. Exposure model (ho)

For this domain, the first prototype does not pretend that all offboarding harms have a meaningful scalar value.

Instead, it uses a constraint vector:

[
ho(q)=
(
U, S, A, P
)
]

where:

- (U): unresolved external-effect obligations;
- (S): stale-authority execution count;
- (A): out-of-scope action count;
- (P): protected-source mutation count.

The hard budget for the prototype is:

```text
S == 0
A == 0
P == 0
U <= U_max
```

`U_max` is a deployment parameter controlling how many unresolved effects may coexist. The default experiment uses `U_max = 1` to force serial reconciliation.

This is intentionally not called a complete harm metric.

## 11. Capability

The offboarding capability binds:

```text
case_id
authority_epoch
obligation_id
subject_ref
target_system
operation
state_version
not_before
expires_at
request_identity
```

It does not grant arbitrary HRIS or IAM access.

## 12. Hold conditions

The BAA instance returns `hold` rather than inventing certainty when:

- effective time has not arrived;
- authoritative time or fact freshness is unavailable;
- the obligation / governance basis cannot be revalidated;
- verification is unavailable for a required effect;
- an effect for the same obligation is already unresolved;
- the protected observation path is degraded;
- the bridge assumptions required for the claimed property are not current.

## 13. Terminal unresolved effects

If the unattended horizon ends while an external effect remains possibly realized but unverified:

- it remains unresolved in the VSAR;
- replay permission is not created;
- its exposure remains charged;
- delivery is incomplete;
- the deployment may enter a safe terminal state.

The effect is not statistically removed from the denominator.

## 14. What is deliberately not guaranteed

This first domain instance does not structurally prove:

- that termination itself is lawful or fair;
- that the selected successor is normatively correct;
- that all organizational knowledge transfer is complete;
- that disabling these interfaces removes every possible access path;
- that provider observations are semantically complete outside (Omega_{mathrm{bridge}});
- that the employee cannot be harmed through communication, reputation, payroll, physical access, or other uncovered channels;
- that external completion implies responsibility discharge.

Those are outside the first guarantee boundary.

## 15. First experiment

The first concrete experiment compares three regimes for the same offboarding episode set:

1. direct agent execution after self-check;
2. direct execution plus external record / post-hoc audit;
3. BAA admission plus exact-scope capability, serial unresolved-effect limit, independent read-back, and conservative pending treatment.

Fault scenarios:

- execution confirmation lost after IAM disable request;
- repeated request after outcome unknown;
- stale authority epoch;
- capability used for another employee;
- capability used for another operation;
- observation source unavailable;
- attempt before effective time;
- protected observation source targeted for mutation;
- model replacement with the same kernel;
- adaptive decomposition / retry probing.

Primary question:

> Under the same offboarding workload, does BAA reduce unsafe reality-facing transitions and unresolved replay risk without causing principal attention or incomplete delivery to dominate?
