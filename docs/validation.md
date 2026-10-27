# Validación de la primera versión

Fecha: 27 de octubre de 2026.

## Verificación ejecutada

- Suite local: **33 tests PASS, sin skips**, ejecutada con Python 3.12, Pillow e imageio-ffmpeg en un entorno virtual temporal aislado.
- Estado editorial: marcas separadas, manual/historial, aprobación ligada al manifiesto y archivos, revocación, offsets/zonas IANA, ventana horaria, reserva concurrente, resultados inciertos y reconciliación.
- Programación: requiere evidencia del servicio; seguimiento a publicado sin repetir el envío y cancelación local sólo después de comprobar cancelación remota.
- Recuperación: permite guardar la evidencia de un envío incierto aunque el archivo visual haya desaparecido después de reservar.
- Instalación: copia completa, CLI instalada ejecutable, rechazo de sobrescritura y de destino symlink.
- Medios: PNG con texto español y fotos proporcionadas sin deformación, errores por entradas inválidas o texto ilegible, MP4 H.264 decodificado con múltiples slides y animación.
- Metadata de skill: `quick_validate.py` pasó. Referencias Markdown locales comprobadas.
- Ejemplo reproducible: genera un paquete ficticio pendiente de aprobación y archivos finales; no opera cuentas.

Comandos:

```bash
python3 -m venv /tmp/cm-master-validation-env
/tmp/cm-master-validation-env/bin/python -m pip install -r requirements.txt -r requirements-media.txt
/tmp/cm-master-validation-env/bin/python -m unittest discover -s tests -v
```

En esta sesión se reutilizó el intérprete `/tmp/cm-master-media-validation/.venv/bin/python`, creado exclusivamente para las pruebas. Las dependencias no se instalaron globalmente.

## Artefacto de medios comprobado

El ejemplo `examples/demo-media.json` produjo PNG y MP4 de 1080×1350. Video H.264, yuv420p, 3 segundos, 24 fps, 72 fotogramas; decodificación completa e inspección visual del PNG y un fotograma. Se comprobó también una imagen de entrada en los tests.

El renderer produce composiciones de texto/fotos y geometría abstracta sin audio. No se presenta como generación de escenas nuevas por IA.

## Evaluación de la skill

Antes de escribir la skill se probaron tres casos sin instrucciones específicas: aprobación antigua con texto cambiado y nota web, falta de herramientas de video/navegador y datos de dos marcas. El agente mantuvo las decisiones correctas de aprobación y procedencia. La skill agrega flujo persistente y contratos concretos; no se añadieron reglas artificiales para fallos no observados.

La evaluación independiente con la skill y la revisión de código se documentarán al completar sus resultados.

## Límites de la evidencia

No se publicaron piezas reales, no se enviaron correos, no se crearon tareas reales y no se usaron cuentas de clientes. El flujo de navegador, correo y tareas requiere configurar las herramientas y sesiones del host, elegir una marca real y autorizar sus operaciones. El paquete no incluye un servicio de publicación ni acceso automático a esas cuentas.

No se ejecutó una sesión real de Claude Code. Su compatibilidad se basa en formato Agent Skills portable, instrucciones por capacidad, instalador y scripts probados localmente. Tampoco se verificó todavía CI remoto en las versiones de Python configuradas; el resultado local no sustituye esas ejecuciones.
