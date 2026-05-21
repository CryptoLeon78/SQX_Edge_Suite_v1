# CFX-TARGET1 - Target SQX Profiles And Cross-Broker OOS2

## Summary

Project Generator now separates two concerns that were previously easy to
confuse:

- Target SQX profile: the broker/source shape used by the recipient's SQX for
  the main generated project resources.
- Methodology cross-broker validation: Retest 1/OOS2, which must stay on
  Dukascopy from `2010.01.01` to `2017.10.02`.

This lets us deliver `.cfx` files to users whose SQX Data Manager uses a broker
other than Darwinex, without destroying the methodological reason for the
Dukascopy retest.

## Target Profiles

Default user-download profile:

- `sq_default_exact`
- broker postfix empty
- broker id `0`
- source id `0`
- Forex `InstrumentInfo` data type `1`, so SQX 142 does not resolve the
  generated symbol as a futures-style resource.
- symbol template `{asset}`; for example `GBPJPY`, not `GBPJPY_darwinex`
- intended for testers/users whose SQX Data Manager shows symbols without
  suffix and broker profile `SQ default`, such as the RILIS compatibility case.

Server/operator profile:

- `sqxedge_darwinex`
- broker postfix `_darwinex`
- broker id `4`
- source id `4`
- intended for the SQX Edge Suite server and the current operator SQX 142 host.
  Use it only when the recipient SQX also has Darwinex-compatible symbols/data.

Manual user-broker profile:

- `custom_user_broker`
- allows exact symbol, broker postfix, broker id, source id, broker name and
  timezone.
- use when the recipient will open the project in a SQX installation whose
  Data Manager does not have Darwinex-compatible symbols.
- exact symbol is preferred when the user's broker does not use a predictable
  postfix convention.

## Protected Methodology Rule

Retest 1 for Capa 1 is not a regular target-host resource. It is:

- label: `Retest 1 / OOS2 Dukascopy`
- broker profile: Dukascopy
- source id: `2`
- broker id: `3`
- period: `2010.01.01 -> 2017.10.02`

The target profile selector must not override this retest. If a generated `.cfx`
uses a primary user broker and Retest 1 uses Dukascopy, that is expected.

## Compatibility Warning

A user may still see SQX's resource resolver if their local SQX does not contain
the selected broker symbols, broker profile or the required historical data.
This is not a security issue; it means the recipient's Data Manager does not
match the profile chosen at generation time.

When this happens, use the manual profile with the exact symbol and
broker/source identifiers from the user's SQX Data Manager, or ask the user to
map the project resource to an existing symbol inside SQX.

RILIS compatibility note:

- If the user's Data Manager shows `Broker profile = SQ default` and symbols
  like `GBPJPY`, choose `SQ default / símbolo exacto`.
- If their Data Manager shows a custom broker name or suffixed symbols, choose
  `Broker del usuario` and enter the exact symbol plus broker/source ids from
  that SQX.
