# CM Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Entregar una skill instalable para Codex y Claude Code que administre marcas locales y coordine contenido final, aprobación, publicación por navegador y análisis.

**Architecture:** Núcleo portable en `skills/cm-master/`, referencias por flujo y adaptadores por host. CLI Python local para estado editorial y huellas de aprobación; renderer independiente para PNG/MP4. El navegador y las tareas programadas pertenecen al host, no a un bot implementado por este repositorio.

**Tech Stack:** Python 3.10+, biblioteca estándar para estado/CLI, Pillow para composiciones, FFmpeg o imageio-ffmpeg para H.264; unittest/pytest para verificación.

**Spec:** `docs/superpowers/specs/2026-10-27-cm-master-design.md`.

## Global Constraints

- Codex y Claude Code; una fuente de skill en `skills/cm-master/`.
- Varias marcas; datos por defecto en `~/.cm-master/brands/<id>/`, raíz configurable.
- LinkedIn, Instagram, Facebook y X, con publicación por navegador disponible y aprobación humana concreta.
- Sin APIs pagas, servidor permanente, envío de correos ni publicaciones reales durante las pruebas.
- MP4 de fotos, textos y animaciones aceptado como alternativa inicial.
- Estado `scheduled` sólo con evidencia del servicio; una fecha local no es programación remota.
- Datos operativos reales fuera del repositorio público.

## Review Focus

- Archivos cambiados después de aprobar: `check` debe invalidar la huella aunque el manifiesto no cambie.
- Interrupción tras enviar: una reserva persistente impide repetir sin reconciliar el destino.
- Rutas/symlinks que apuntan a otra marca: rechazar antes de leer o escribir medios.
- Fechas sin offset o con zona contradictoria: rechazar; nunca publicar una pieza vencida automáticamente.
- Falta de navegador/generador/tarea persistente: declarar la capacidad faltante y conservar el paquete, sin simular ejecución.

## Interfaces compartidas

CLI: `python skills/cm-master/scripts/cm.py --root DIR <command> ...`. `--root` es opcional y equivale a `CM_MASTER_HOME` o `~/.cm-master`.

Comandos: `init-brand ID --name NAME [--website URL]`, `list-brands`, `profile ID [--file JSON]`, `draft ID POST --file JSON`, `stage ID POST --file JSON`, `review ID POST`, `approve ID POST --review-sha SHA --evidence TEXT --by NAME`, `revoke ID POST --reason TEXT`, `check ID POST [--mode publish|schedule]`, `begin ID POST [--mode publish|schedule]`, `record ID POST --status published|scheduled|uncertain|blocked --evidence TEXT [--url URL] [--reconciled]`, `resolve ID POST --outcome not-published --evidence TEXT`, `cancel-scheduled ID POST --evidence TEXT`, `due [--brand ID]`.

Manifiesto de pieza: `network` (`linkedin|instagram|facebook|x`), `account` (URL exacta), `format` (`feed|story|reel|carousel|video`), `scheduled_at` (ISO 8601 con offset), `timezone` (IANA), `text`, `alt_text`, `media` (lista de rutas relativas a la carpeta de marca), y opcionales `objective`, `sources`, `brief`. Conservar el paquete en `posts/<post>/post.json`. `review` devuelve la huella canónica y los detalles aprobables; `approve` exige esa huella actual y evidencia humana. La CLI no autentica al humano ni opera el navegador.

`check --mode publish` admite la ventana desde el horario aprobado hasta 60 minutos después; `schedule` sólo fechas futuras. Pasada la ventana, reprogramar y volver a aprobar. `begin` hace comprobación y reserva exclusiva persistente antes de la acción externa. Una segunda reserva, `scheduled`, `published`, `uncertain` o `blocked` impiden repetir. `resolve` con evidencia de ausencia permite volver a un estado aprobable; nunca reintentar automáticamente un envío incierto.

Renderer: `python .../render_media.py SPEC.json --output PATH [--kind image|video]`. Spec incluye `brand_name`, `headline`, `body`, `cta`, `background`, `foreground`, `accent`, `size: [w,h]`, `slides` (texto y `image` opcionales) y `seconds_per_slide`; imágenes relativas al spec. Exporta PNG o MP4 real y falla claramente si falta una dependencia. No necesita el módulo de estado.

### Task 1: Estado editorial, aprobación y reserva

**Files:** `skills/cm-master/scripts/cm.py`, `skills/cm-master/scripts/cm_state.py`, `tests/test_state.py` (contratos de estado y CLI en subprocesos).

**Interfaces:** produce la CLI y manifiesto indicados arriba, JSON de salida y exit code no cero ante estado inválido. Sin dependencias externas.

- [x] Escribir tests de aislamiento, perfil/historial, aprobación ligada a texto/medios/cuenta/fecha, revocación y datos incompletos.
- [x] Ejecutar `python3 -m unittest discover -s tests -p 'test_state.py' -v` y observar FAIL antes de implementar.
- [x] Implementar persistencia atómica con un lock local, validación de rutas/IDs y zona horaria, revisión, reserva y reconciliación.
- [x] Probar CLI en subprocesos con raíces temporales, doble reserva, snapshots públicos y cola `due` sin efectos externos.
- [x] Ejecutar los tests y confirmar PASS; documentar el contrato operativo.

### Task 2: Archivos visuales finales

**Files:** `skills/cm-master/scripts/render_media.py`, `tests/test_media.py`, `examples/demo-media.json`, `requirements-media.txt`.

**Interfaces:** renderer independiente del estado, según contrato compartido. Spec relativo al directorio de entrada, sin red ni IA paga.

- [x] Escribir pruebas que abran un PNG y verifiquen tamaños, texto largo/acentos y error de specs inválidos.
- [x] Ejecutar pruebas y observar FAIL por renderer ausente.
- [x] Implementar composición Pillow y animación local codificada en MP4 con FFmpeg o imageio-ffmpeg. Soportar imágenes de marca sin deformarlas y detección clara de dependencias.
- [x] Ejecutar pruebas y renderizar un MP4 real ficticio; comprobar reproducción, duración y dimensiones. Inspeccionar una imagen y un fotograma.

### Task 3: Skill y referencias operativas

**Files:** `skills/cm-master/SKILL.md`, `agents/openai.yaml`, `references/{onboarding,editorial,publishing,analytics,hosts,local-tools}.md` bajo esa skill.

**Interfaces:** consume la CLI y spec del renderer anteriores; usa las herramientas reales enumeradas por cada host. La selección automática sigue habilitada.

- [x] Ejecutar escenarios baseline sin la skill y registrar decisiones observadas.
- [x] Escribir instrucciones de entrevista, manual con fuentes/certeza, calendario, contenido original, aprobación y publicación verificable. Usar referencias condicionales, no cargar todo siempre.
- [x] Cubrir tendencias actuales, competencia, métricas con denominador, historial y aprendizajes; configuración de correo/tareas por marca sin crearlos durante instalación.
- [x] Validar metadata con `quick_validate.py` y ejecutar escenarios independientes con la skill, sólo en sandbox de datos ficticios.

### Task 4: Instalación, ejemplo y entrega

**Files:** `scripts/install.py`, `tests/test_install.py`, `tests/test_package.py`, `README.md`, `.github/workflows/test.yml`, `docs/validation.md`, ejemplos ficticios.

**Interfaces:** instalador copia la misma carpeta en `~/.agents/skills/cm-master` (Codex) o `~/.claude/skills/cm-master` (Claude). `--destination PATH` para prueba; rechaza destino existente, sin sobrescribir. No cambia settings, permisos, tareas o cuentas.

- [x] Escribir y observar fallar pruebas de instalación completa y rechazo de sobrescritura.
- [x] Implementar instalador, README en español con instalación, invocación y ejemplo reproducible de ciclo editorial; CI sin cuentas externas.
- [x] Ejecutar suite completa, validación de skill, render real y revisión independiente contra el diseño.
- [x] Corregir hallazgos materiales con pruebas, verificar estado limpio y publicar commits en el repositorio autorizado. Registrar límites de validación reales, sin afirmar haber probado cuentas o Claude en vivo.

## Decisiones de ejecución

- El usuario ya pidió implementar: ejecutar sin otra ronda de aprobación del plan técnico.
- Reutilizar el checkout limpio en una rama de trabajo; el repositorio recién creado sólo contiene nuestro diseño y no requiere otra copia del proyecto.
- Delegar los componentes independientes de medios y documentación en paralelo; el controlador implementa estado y empaquetado. Compartir contratos, no archivos de implementación.
- Las pruebas no publican en redes, no envían emails y no crean tareas reales.

## Ajustes comprobados durante implementación

- Las pruebas independientes demostraron que faltaba conservar borradores sin cuenta/fecha. `draft` conserva datos parciales y `delivery_due_at` sin inventar fecha de publicación; `due` los muestra como no ejecutables. `stage` exige completar el contrato antes de obtener una revisión aprobable.
- La revisión de código detectó que `revoke` permitía evitar la reconciliación desde `blocked`; se protege también ese estado y el test reprodujo la falla antes de corregirla.
- Para una salida remota comprobada cuyo medio local cambió, `record --reconciled` cierra sólo un resultado incierto con evidencia explícita y conserva la advertencia/versiones. No vuelve a aprobar el paquete local modificado.
- Los requirements viajan dentro de la skill instalada; los archivos de raíz los incluyen sin duplicar versiones.
- Archivos ajenos como `.DS_Store` no interrumpen el listado de marcas/paquetes.

## Cierre

Tareas 1–4 implementadas, revisión independiente y prueba funcional completadas. Suite final local: 38 tests PASS, sin skips. Código integrado por fast-forward en main del repositorio nuevo y subido a GitHub. No se modificaron archivos de marcas reales, configuraciones globales ni cuentas externas.
