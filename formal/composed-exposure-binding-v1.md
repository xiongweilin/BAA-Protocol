# Composed Exposure Binding v1

> English | [简体中文](composed-exposure-binding-v1.zh-CN.md)

## Status

This result closes one finite refinement obligation for the offboarding prototype: a reality-side exposure measurement is now tied to the exact BAA proposal that was admitted before the real product effect.

The accepted implementation is AIOS `b2cc1254a1908d00ded7c705f6e230c43f08f6f8`. The qualifying real-product E2E ran on PR head `e10c5f6c52e12ea08f603e9c8d01ca099e070df4`. Both commits have the identical Git tree `0b24ed3f205ad8bbeffd6b238738baa1a34564a0`, so the tested code content is exactly the code accepted into AIOS main.

The E2E pinned BAA `b3215d940cf7c9bd6b208ed5915eaa3c92ab10e3`.

The machine-readable record is [composed-exposure-binding-v1-result.json](composed-exposure-binding-v1-result.json).

## What is now connected

For each of the three covered real product effects:

1. AIOS creates an effect with a stable `effect_id`.
2. The BAA gate constructs the actual proposal id as `effect:{effect_id}`.
3. The gate emits an `admit` refinement event for that proposal before dispatch.
4. The acceptance controller keeps a before/after census of the frozen managed-subject state projection.
5. Reality-side evidence emits the same proposal id, subject, metric id, changed-subject set, and realized exposure.
6. The E2E reconstructs the proposal through the real gate, obtains `exposure_declaration_for_proposal()`, and evaluates `assess_metric_bound()`.
7. Only an established assessment is converted by `realized_exposure_for_settlement()`.

The frozen metric is `managed-subject-state-change-count-v1`; all three offboarding proposal classes declare bound 1.

## Qualifying run

AIOS workflow run `37638217335` passed all four scenarios.

For `normal`, `lost_ack`, and `readback_outage`:

- `identity.disable`: declared bound 1, realized exposure 1;
- `sessions.revoke`: declared bound 1, realized exposure 1;
- `employee.deactivate`: declared bound 1, realized exposure 1;
- every assessment is established;
- every measured proposal occurs in the gate's actual `admit` trace;
- Keycloak measurements enumerate 2 managed subjects and change only the declared target;
- Odoo measurements enumerate 3 employee subjects and change only the declared target.

The recovery scenarios finish through `executing -> completed`, so lost acknowledgement and temporary read-back loss do not break proposal identity or exposure accounting.

The `runtime_bypass` scenario returns HTTP 403 at the authorization boundary, observes no provider effect, and preserves the target product state.

Artifacts:

- normal: `11491082646`, digest `sha256:f9f307627a55b01c38c78dc3603019ed6526e71b11f6af0ba02067c3a173e5b5`;
- lost_ack: `11489419994`, digest `sha256:7252a32f9ab63f63a3c481be247a83574be84c0c67a505add493b290d1925325`;
- readback_outage: `11489454782`, digest `sha256:e44102ff8443f0f7c8ee76b1c2e1e631d55ba09461284ab7ce9c3a65b26c343a`;
- runtime_bypass: `11489744687`, digest `sha256:a83371e4d8138a2f7eb1abf70861a9a79dafbcc8c88826caa6f0f4b4197e84cb`.

## Evidence roles

Two evidence roles remain deliberately distinct.

The normal target postcondition read-back still uses separate read-only verifier credentials. The managed-subject scope census is acceptance instrumentation using the isolated ephemeral product controller, because its purpose is to establish completeness of the frozen test projection.

This is sufficient for a finite acceptance claim. It is not a deployed guarantee-channel design.

## What this result establishes

Within the frozen offboarding domain, acceptance products, metric, state projection, and tested scenarios, the chain

`admitted proposal -> declared metric/bound -> real effect -> scope-complete measurement -> bound assessment`

is executable and passes for all three covered operations, including the two ambiguity-recovery scenarios.

The previous gap "the measurement has no admitted proposal identity" is therefore closed for this finite composed path.

## What remains open

This result does not establish:

- absence of changes to hidden product fields;
- absence of effects on unrelated object types, unmanaged subjects, external services, or downstream systems;
- completeness of this census mechanism in production tenants;
- that one changed subject corresponds to a calibrated amount of harm;
- that different unit exposures interact according to the current structural joint-risk function;
- production safety.

The highest-value remaining semantic obligation is now the last two items: justify the mapping from the frozen exposure metric to the loss/risk quantity of interest, especially its composition across multiple admitted effects.

That obligation should not be discharged by adding more successful connector fixtures. It requires an explicit loss model or a deliberately weaker guarantee claim.
