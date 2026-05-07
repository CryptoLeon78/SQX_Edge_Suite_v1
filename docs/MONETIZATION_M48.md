# Monetization Phase M48 - Basic Buyer Onboarding And Support Gate

Fecha: 2026-05-07.
Estado: Done.

## Objetivo

Preparar una entrada basica para comprador Pro: compra confirmada, ZIP, licencia, instrucciones de arranque, FAQ, soporte inicial y criterios claros de pausa o reembolso.

## Entregables

- Estado `buyer_onboarding_support_gate_ready`.
- Configuracion `backend/sqx-edge-tool/config/buyer_onboarding_support_gate.json`.
- Recursos buyer-facing en `resources/pro-buyer-pack/onboarding`, incluido `START_HERE.md`.
- Guia interna `docs/sales/BUYER_ONBOARDING_SUPPORT_GATE.md`.
- Validador interno `backend/sqx-edge-tool/tools/buyer_onboarding_support_gate.py`.
- Exclusiones de packaging para evidencia y herramienta interna.

## Decision

El onboarding basico viaja en el portable para que el comprador pueda empezar sin Python ni conocimiento tecnico. La herramienta de gate y la evidencia local quedan fuera del ZIP final.

## Criterios

- No entregar sin ZIP, licencia, instrucciones y FAQ.
- No escalar sin soporte inicial preparado.
- No prometer rentabilidad, senales, estrategias ganadoras ni asesoramiento financiero.
- Si el comprador esperaba resultados financieros, la respuesta correcta es aclarar alcance, pausar o revisar reembolso.
