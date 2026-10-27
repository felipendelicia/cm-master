# Validación de la primera versión

Fecha: 27 de octubre de 2026.

## Verificación ejecutada

- Suite local final: **38 tests PASS, sin skips**, ejecutada con Python 3.12, Pillow e imageio-ffmpeg en un entorno virtual temporal aislado.
- Estado editorial: marcas separadas, manual/historial, aprobación ligada al manifiesto y archivos, revocación, offsets/zonas IANA, ventana horaria, reserva concurrente, resultados inciertos y reconciliación.
- Programación: requiere evidencia del servicio; seguimiento a publicado sin repetir el envío y cancelación local sólo después de comprobar cancelación remota.
- Recuperación: permite guardar la evidencia de un envío incierto aunque el archivo visual haya desaparecido después de reservar.
- Instalación: copia completa, CLI instalada ejecutable, rechazo de sobrescritura y de destino symlink.
- Portabilidad del paquete: manifiestos de dependencias incluidos dentro de la skill instalada; sin depender del clon original.
- Borradores: datos parciales, plazo de entrega separado de fecha de publicación y cola no ejecutable hasta completar revisión.
- Archivos auxiliares como `.DS_Store` no interrumpen el listado de marcas y paquetes.
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

Un agente independiente utilizó la skill para dos marcas ficticias, Faro Café y Río Software. Persistió sus manuales por separado, produjo una imagen 1080×1350 y un reel MP4 H.264 de 1080×1920, 9 segundos y 216 fotogramas, e inspeccionó visualmente el contenido y la decodificación completa. Preparó calendario de cuatro semanas, tanda de siete días y propuesta de medición; mantuvo las métricas desconocidas como no disponibles.

La primera prueba encontró que no se podían guardar paquetes sin cuenta exacta ni fecha de salida. Se implementó `draft`; una segunda prueba funcional confirmó ambos borradores persistidos sin inventar esos datos, `due` con `ready: false` y rechazo de los cuatro intentos de `begin` en ambos modos. Los medios y manuales conservaron sus hashes. El plazo «listo mañana a las 11» se conservó como `delivery_due_at`, no como autorización para publicar.

La revisión independiente de código encontró dos problemas materiales: `revoke` permitía evitar la reconciliación desde `blocked`, y un medio cambiado impedía cerrar un resultado remoto verificado. Ambos se reprodujeron con tests que fallaron antes de corregirlos. Se protegió el estado bloqueado y se agregó `record --reconciled` para resultados inciertos verificados, conservando la huella del intento y quitando la aprobación del paquete local cambiado. Se comprobó también cierre de publicación observada desde `blocked` y cancelación remota comprobada tras reconciliar.

Los medios del renderer usan una composición base configurable, sin audio; antes de aprobar una pieza para una cuenta real se debe revisar su encuadre y las superposiciones del editor de esa red. Estas pruebas no verifican las áreas visibles de Instagram u otra interfaz real.

## Límites de la evidencia

No se publicaron piezas reales, no se enviaron correos, no se crearon tareas reales y no se usaron cuentas de clientes. El flujo de navegador, correo y tareas requiere configurar las herramientas y sesiones del host, elegir una marca real y autorizar sus operaciones. El paquete no incluye un servicio de publicación ni acceso automático a esas cuentas.

No se ejecutó una sesión real de Claude Code. Su compatibilidad se basa en formato Agent Skills portable, instrucciones por capacidad, instalador y scripts probados localmente.

GitHub Actions también completó **38 tests PASS, sin skips, tanto en Python 3.10 como en Python 3.12**, para el commit de implementación `b39e6890a9703164a7b770b6b4b3261bb712f756`. [Ejecución remota verificada](https://github.com/felipendelicia/cm-master/actions/runs/40571089428). Los cambios posteriores a ese commit son únicamente este registro de validación y el cierre documental del plan.
