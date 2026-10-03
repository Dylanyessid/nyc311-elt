## Lag de publicación en Socrata

El 2026-09-29, un día después de ocurrido, el endpoint solo tenía 456 de
los 11.905 registros finales (4%). Tres días después estaban completos.

Implicación: el DAG no debe procesar D-1. Usar un desfase de al menos D-3
y reprocesar una ventana móvil de ~10 días en cada corrida para capturar
registros rezagados.