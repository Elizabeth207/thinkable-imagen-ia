# Contexto del proyecto

## Objetivo

Sistema Inteligente de Mejora de Imágenes con IA, de THINKABLE LABS OPERATIONS S.A.C. Es una aplicación web local: el usuario sube una imagen, el sistema la mejora con una API externa de inteligencia artificial y guarda el historial. No se entrenan modelos propios.

## Restricciones

- Sin modelos propios. La mejora la hace un proveedor externo.
- Sin pagos ni créditos dentro del sistema.
- Sin microservicios. `motor-ia` es un paquete Python que usa `servidor-api`, no un servicio aparte.
- Sin Kubernetes ni orquestación de contenedores.

## Ejecución

Todo se ejecuta en la máquina local: interfaz, backend Flask y base de datos PostgreSQL. No hay despliegue en la nube en esta etapa.
