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
- broker id `-1` (SQX internal no-broker/default profile; avoids `BrokerDto`
  null errors on recipient machines that do not have a real broker row for
  `SQ default`)
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
- Retest 1/OOS2 keeps Dukascopy bars (`source=2`, `{asset}_dukascopy`) but
  uses the Darwinex execution resource (`broker=4`, `{asset}_darwinex`) for
  this target, even when generation runs without direct access to the
  operator's local `data.db`.
- Generated projects for this profile strip packaged `<CustomBlocks>` donor
  definitions. The operator SQX142 installation owns those snippets locally;
  carrying donor copies can trigger SQX's `Undefined / different blocks found`
  resolver and fail while updating the loaded project.

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
- data source: Dukascopy
- source id: `2`
- default pure broker id: `3`
- period: `2010.01.01 -> 2017.10.02`

The target profile selector must not override this retest. If a generated `.cfx`
uses a primary user broker and Retest 1 uses Dukascopy, that is expected.

Operator-local hybrid convention:

- Some SQX 142 Data Manager assets intentionally store `SYMBOL={asset}_dukascopy`
  with `DATA.SOURCE=2` while `DATA.INSTRUMENT={asset}_darwinex` and
  `DATA.BROKER_ID=4`.
- This means Retest 1 uses Dukascopy candles under Darwinex execution
  assumptions: spread, commissions, swap, tick size and broker resource remain
  Darwinex.
- The generator preserves this when `data.db` exposes the hybrid row:
  chart/resource symbol stays `{asset}_dukascopy`, source stays `2`, resource
  broker becomes the inherited Darwinex broker, and `InstrumentInfo` comes from
  `{asset}_darwinex`.
- This is not a broker-robustness claim. It is a data-vendor/OOS candle
  validation under the current Darwinex execution model, and must be described
  that way in evidence.

When SQX `data.db` is available during generation, the generator checks the real
Dukascopy/OOS2 coverage for the selected asset. If the local data starts later
than the canonical 2010 start but still gives at least two years of historical
pre-Build coverage, Retest 1 is bounded to the real available range. If coverage
is missing or too short, generation must fail before SQX import instead of
creating a project that opens with unresolved resources.

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
- If the operator/local SQX142 Data Manager shows symbols such as
  `AUDCAD_darwinex` and cross-provider data such as `AUDCAD_dukascopy`, choose
  `SQX Edge / Darwinex`.
- If SQX first reports resources resolved and then shows custom blocks as
  `Different`, regenerate with `SQX Edge / Darwinex` after this profile fix so
  SQX uses its installed snippets instead of donor-packaged block definitions.
- If their Data Manager shows a custom broker name or suffixed symbols, choose
  `Broker del usuario` and enter the exact symbol plus broker/source ids from
  that SQX.
