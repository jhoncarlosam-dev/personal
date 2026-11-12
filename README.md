# Hojas de vida — Jhon Carlos Acevedo Mendoza

Dos versiones, noviembre de 2026. Cada una se envía según el cargo. No se mezclan.

| Cargo | Archivo para enviar |
| --- | --- |
| Desarrollador backend | [cv/Hoja-de-vida-Jhon-Acevedo-Backend.pdf](cv/Hoja-de-vida-Jhon-Acevedo-Backend.pdf) |
| Analista de calidad (QA) | [cv/Hoja-de-vida-Jhon-Acevedo-QA.pdf](cv/Hoja-de-vida-Jhon-Acevedo-QA.pdf) |

El HTML de la misma carpeta es la fuente. El PDF es el que se adjunta.

## Qué CV usar

La de QA es la más fuerte hoy: describe el trabajo actual en Nelumbo, con clientes en México y Europa. Úsala para vacantes de QA manual, QA funcional o QA con automatización inicial.

La de backend es la del objetivo. Úsala para vacantes junior de backend o de desarrollo de software. Se apoya en Arrenda y en Taller Norte, que son APIs públicas, y en el tiempo de Laravel y MySQL en Inglés Para Todos. No presenta Spring Boot como experiencia laboral.

## Al aplicar

Backend:

> Hola. Soy Jhon Acevedo, de Cúcuta. Hoy trabajo como analista de calidad en plataformas SaaS y estoy buscando un rol de desarrollador backend. Adjunto mi hoja de vida. Los proyectos que mejor muestran cómo programo son Arrenda (FastAPI, MySQL, JWT y Pytest) y Taller Norte (Express, PostgreSQL y reservas sin cruce de horario). Quedo atento.

QA:

> Hola. Soy Jhon Acevedo. Trabajo como analista de calidad en Nelumbo, en proyectos para México y Europa (CheckPlus, Obras e IDP). Hago pruebas funcionales, de regresión y exploratorias, documento en Jira y estoy armando automatización con Playwright. Adjunto mi hoja de vida.

## Decisiones que conviene revisar

- El correo es el de la hoja de vida anterior, `jhoncarlosam001@gmail.com`. En [ac3.netlify.app](https://ac3.netlify.app/) aparece `jhoncarlosacevedomendoza@gmail.com`. Conviene usar uno solo.
- La ciudad del encabezado es Cúcuta, como en LinkedIn. El trabajo independiente queda en Arboledas.
- El inglés quedó en A2/B1, como dice el sitio personal. La hoja anterior decía «fluido».
- UNAD quedó «en curso». El sitio dice «etapa final»; no lo afirmé porque es fácil de contrastar.
- UFPS quedó como estudios cursados, 2017–2025, sin título. Si el año de salida es otro, hay que corregirlo en LinkedIn y aquí.
- Café Marrón no está descrito como fullstack: el sitio publicado es HTML, CSS y Bootstrap.
- Spring Boot no está en habilidades. Hay una calculadora de sueldos muy corta en ese stack; no alcanza para defenderla en una entrevista.
- No entran certificados de management ni de finanzas de la Universidad de Palermo, ni el curso de IA de BIG school. Si una vacante los pide, se agregan.

## Siguiente proyecto, antes de ampliar la hoja de backend

Las pruebas técnicas que llegaron de compañeros son material de práctica, no proyectos para publicar tal cual. Varias son enunciados de ingreso y no deben subirse a un repositorio público.

El hueco concreto para un rol backend en el estilo de esos enunciados es una API en Java y Spring Boot, con PostgreSQL, que se pueda clonar y correr. Cuando exista, la hoja de backend gana una línea en Proyectos. Hasta entonces, esa línea no está.

Un buen primer ejercicio, en privado, es un sistema de parqueaderos o de reservas con este alcance:

- autenticación JWT y dos roles
- reglas de cupo, horario o cobro, con histórico
- capas separadas, DTOs y errores consistentes
- diagrama entidad-relación, colección de Postman, Docker y algunas pruebas

Arrenda ya demuestra que ese tipo de sistema se puede construir en Python. El ejercicio nuevo demuestra el stack que piden las pruebas.
