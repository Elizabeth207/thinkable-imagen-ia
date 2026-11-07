# Sistema Inteligente de Mejora de Imágenes con IA

Aplicación web local de THINKABLE LABS OPERATIONS S.A.C. El usuario sube una imagen, el sistema la mejora mediante una API externa de inteligencia artificial y guarda el historial del trabajo.
No se entrenan modelos propios: la mejora la realiza el proveedor configurado.
El proyecto se organiza en tres partes independientes que se ejecutan en la máquina local.

| Parte | Responsabilidad |
| --- | --- |
| portal-web | Interfaz de usuario (frontend). |
| servidor-api | Backend Flask: usuarios, permisos, base de datos y trabajos de procesamiento. |
| motor-ia | Conexión con el proveedor externo de mejora de imágenes. Paquete Python independiente; lo usa servidor-api. No es un microservicio. |
