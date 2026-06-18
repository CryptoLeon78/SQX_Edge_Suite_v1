<!--
  Propuesta de docs/INDEX.md - mapa maestro de la documentacion.
  Colocar en: docs/INDEX.md  (los enlaces relativos asumen esa ubicacion).
  Generado a partir del inventario verificado 2026-06-17.
-->

# SQX Edge Suite v1 - Indice de Documentacion

Mapa maestro para localizar cada **vertical** del proyecto. La doc se nombra por **prefijo = vertical** (`J*`, `SB*`, `T*`, `A*`, `R*`, `MONETIZATION_M*`).
Convencion: el repo **publico** mantiene el contenido operativo; la capa comercial vive **redactada** apuntando al repo privado `sqx-edge-commercial-private`.

---

## Empezar aqui
| Doc | Para que |
|---|---|
| [README_SETUP.md](README_SETUP.md) | Arranque basico (doble-click `START_SQX_EDGE.bat`, Python embebido, empaquetado). Ver nota de setup tecnico abajo. |
| [../README.md](../README.md) | Vision general: dashboard + herramienta local del pipeline SQX Edge. |
| [DISCIPLINA_OPERATIVA.md](DISCIPLINA_OPERATIVA.md) | Estandar de trabajo obligatorio (reglas de proceso). |

> **Setup tecnico (vinculacion SQX path -> `data.db` -> `config.json`):** el flujo `autodetect -> validate -> POST /api/config` (clave `sqx_data_db`) **no estaba documentado** hasta esta entrega. Es lo que desbloquea `symbol-info` y la Auditoria 6/6. Ver `README_SETUP.md`.

## Nucleo tecnico (contenido real)
| Doc | Para que |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Mapa de arquitectura y orden de carga tras la modularizacion. |
| [MODULARIZATION_NEXT_STEPS.md](MODULARIZATION_NEXT_STEPS.md) | Nota de planificacion persistente de proximas fases. |
| [../backend/sqx-edge-tool/README.md](../backend/sqx-edge-tool/README.md) | API/CLI local que genera `.cfx` y lee la `data.db` de SQX. |
| [../backend/sqx-edge-relay/README.md](../backend/sqx-edge-relay/README.md) | Relay remoto (Render) de webhooks Lemon Squeezy / fulfillment. |
| [../CHANGELOG.md](../CHANGELOG.md) | Historial de cambios (fichero mas grande del repo). |

## Gobernanza y decisiones
| Doc | Para que |
|---|---|
| [PROJECT_GOVERNANCE.md](PROJECT_GOVERNANCE.md) | Documento vivo de coordinacion de agentes especializados. |
| [decisions/ADR-0001-specialist-agent-governance.md](decisions/ADR-0001-specialist-agent-governance.md) | ADR-0001 - Gobernanza de agentes especialistas (2026-05-07). |
| [PUBLIC_ROADMAP.md](PUBLIC_ROADMAP.md) | Roadmap publico. |

## Verticales por fase (series con contenido real)
| Serie | Ficheros | Vertical |
|---|---|---|
| **J** | `J1_*.md ... J11_*.md` (11) | Champion/Challenger + EGT Temporal Health (contratos de fase). |
| **SB** | `SB1_*.md ... SB17_*.md` (17) | Strategy Builder (Discovery -> Evidence Handoff). |
| **T** | `T1_*.md ... T10AH_*.md` (~40) | Cloud Tester / Vercel / Cloudflare / Staging. |
| **A** | `A59_*.md ... A62_*.md` (4) | Real Data / MT5. |
| **R** | `R44_*.md`, `R45_*.md`, `R47_*.md` (+A63) | Portable / Controlled Publication / Controlled Release. |
| **PG** | `PG7_*.md` (1) | Project Generator - handoff de `.cfx` a comprador. |

## Capa comercial - superficie publica
| Doc | Para que |
|---|---|
| [COMMERCIAL_README.md](COMMERCIAL_README.md) | Borrador del README comercial (SQX Edge Pro). |
| [PUBLIC_COMMERCIAL_POINTERS.md](PUBLIC_COMMERCIAL_POINTERS.md) | Punteros publicos tras la redaccion S5. |
| [PRIVATE_COMMERCIAL_DOCS.md](PRIVATE_COMMERCIAL_DOCS.md) | Frontera de docs comerciales privados. |
| [PRIVATE_COMMERCIAL_SPLIT_PLAN.md](PRIVATE_COMMERCIAL_SPLIT_PLAN.md) | Plan del split publico/privado (`private_repo_published`). |
| [EXTERNAL_REPO_COMPARISON_JOSE.md](EXTERNAL_REPO_COMPARISON_JOSE.md) | Comparacion con `jlivanmaseda-maker/sqx-edge-pipeline`. |

## Redactado a repo privado (NO borrar - punteros intencionales)
Punteros de la fase **S5** -> contenido real en `github.com/CryptoLeon78/sqx-edge-commercial-private`:

| Zona | N | Contenido |
|---|---|---|
| `MONETIZATION_M1.md ... M99.md` + `MONETIZATION_ROADMAP.md` | 99+ | Punteros identicos redactados. |
| `sales/*` | ~60 | Fulfillment / relay / Render / Vercel - redactados. |
| `../resources/pro-buyer-pack/**`, `pro-template-pack-1/**`, `pro-template-pack-2/**` | varios | Onboarding y packs de comprador - redactados. |
| [../templates/SQX_Edge_Tester_Portal/README.md](../templates/SQX_Edge_Tester_Portal/README.md) | 1 | Bootstrap del portal tester (futuro, en privado). |

> Estos ficheros existen como **punteros** (`"This public file is intentionally redacted."`). Mantienen rutas originales (`Original path: docs/MONETIZATION_Mx.md`) para el mapeo publico<->privado: **moverlos o borrarlos rompe la redaccion**.

---

## Pendientes de doc (gaps detectados 2026-06-17)
1. **Colision de puerto `:5050`** con SQX - documentada ahora en `README_SETUP.md`; queda pendiente la decision de hacer el puerto configurable (aparcada).
2. `docs/design_concepts/` - directorio presente; sin inventariar en este indice.

## Leyenda
`J`=Champion/Challenger | `SB`=Strategy Builder | `T`=Cloud Tester | `A`=Real Data/MT5 | `R`=Releases | `PG`=Project Generator | `MONETIZATION_M`/`sales`/`resources`=comercial **redactado**.
