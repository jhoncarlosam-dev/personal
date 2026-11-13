# Prueba técnica — Ruta Norte

API para agendar clases de una escuela de conducción. El ejercicio está armado con lo que se repite en las vacantes de Java: Spring Boot, Spring Security, PostgreSQL, una regla de negocio y pruebas.

Arrenda y Taller Norte ya cubren la idea en Python y en Node. Aquí el aprendizaje nuevo es el stack de Java.

## Qué queda fuera

Estas piezas salen en una sola oferta, no en el grupo. No las estudies para esta prueba.

- C# y .NET
- Vue 3 y Google Cloud
- Kubernetes
- DynamoDB
- Un segundo microservicio

## Stack

- Java 17
- Spring Boot 3
- Spring Web, Spring Security, Spring Data JPA, Validation
- PostgreSQL 16
- JWT (access token, expiración de 6 horas)
- JUnit 5
- Docker Compose para la base
- Maven

Contraseña con BCrypt. El secreto del JWT y la clave del admin salen de variables de entorno, no van escritas en el código.

## Historia

Ruta Norte tiene instructores y vehículos. Una clase dura 60 minutos, usa un instructor y un vehículo, y tiene un alumno identificado por documento.

Hay dos roles.

**ADMIN**

- Crea instructores.
- Crea vehículos y les define el precio de la hora en pesos.

**INSTRUCTOR**

- Agenda una clase a su nombre.
- Ve solo sus clases.
- Cancela una clase suya que todavía no empieza.
- Consulta cuánto suman hoy sus clases no canceladas.

Un instructor no administra vehículos ni crea otros instructores.

## Datos

Usuario:

- correo, único
- nombre
- contraseña
- rol: `ADMIN` o `INSTRUCTOR`

Vehículo:

- placa, única
- tipo de caja: `MANUAL` o `AUTOMATICA`
- precio por hora, entero mayor que cero
- activo, verdadero o falso

Clase:

- instructor
- vehículo
- documento del alumno, de 6 a 12 dígitos
- nombre del alumno
- inicio, fecha y hora
- fin, calculado: inicio más 60 minutos
- estado: `RESERVADA` o `CANCELADA`
- valor cobrado: el precio por hora del vehículo en el momento de agendar

## Reglas

1. El admin inicial se crea al arrancar, leyendo correo y contraseña del entorno.
2. Toda ruta, menos el login, exige un JWT válido.
3. Una clase solo se agenda si el inicio es posterior al momento de la petición.
4. El vehículo tiene que existir y estar activo.
5. El mismo instructor no puede tener dos clases `RESERVADA` que se crucen en el tiempo.
6. El mismo vehículo no puede tener dos clases `RESERVADA` que se crucen, aunque el instructor sea otro.
7. Cancelar una clase ajena responde 403.
8. Cancelar una clase que ya empezó responde 409.
9. Una clase `CANCELADA` no se vuelve a reservar y no entra en el total del día.
10. El total del día cuenta las clases `RESERVADA` cuyo inicio cae en la fecha local de America/Bogota.

Dos intervalos se cruzan cuando uno empieza antes de que el otro termine. Una clase de 10:00 a 11:00 y otra de 11:00 a 12:00 no se cruzan.

## API

Base: `/api`

Los cuerpos usan JSON. Las fechas van en ISO-8601 con zona, por ejemplo `2026-11-20T10:00:00-05:00`.

### POST `/api/auth/login`

Público.

```json
{ "email": "admin@rutanorte.test", "password": "..." }
```

Respuesta 200:

```json
{ "token": "", "expiresInHours": 6, "role": "ADMIN" }
```

Correo o contraseña incorrectos: 401.

```json
{ "mensaje": "Correo o contraseña incorrectos" }
```

### POST `/api/instructors`

Solo `ADMIN`.

```json
{ "name": "Ana Pérez", "email": "ana@rutanorte.test", "password": "un-secreto-largo" }
```

Respuesta 201:

```json
{ "id": 0, "name": "Ana Pérez", "email": "ana@rutanorte.test", "role": "INSTRUCTOR" }
```

Correo repetido: 409, con un mensaje claro.

### POST `/api/vehicles`

Solo `ADMIN`.

```json
{ "plate": "ABC123", "transmission": "MANUAL", "hourlyPriceCop": 80000 }
```

Respuesta 201 con el vehículo creado, `active: true`.

Placa repetida: 409. Precio menor o igual a cero: 400.

### GET `/api/vehicles`

Cualquier usuario autenticado. Devuelve la lista, incluidos los inactivos.

### POST `/api/lessons`

Solo `INSTRUCTOR`. El instructor es el del token. No se acepta un instructor en el cuerpo.

```json
{
  "vehicleId": 1,
  "studentDocument": "1094123456",
  "studentName": "Luis Gómez",
  "startsAt": "2026-11-20T10:00:00-05:00"
}
```

Respuesta 201:

```json
{
  "id": 0,
  "vehiclePlate": "ABC123",
  "studentDocument": "1094123456",
  "studentName": "Luis Gómez",
  "startsAt": "2026-11-20T10:00:00-05:00",
  "endsAt": "2026-11-20T11:00:00-05:00",
  "status": "RESERVADA",
  "priceCop": 80000
}
```

Cruce de instructor: 409 y `"El instructor ya tiene una clase en ese horario"`.

Cruce de vehículo: 409 y `"El vehículo ya tiene una clase en ese horario"`.

Vehículo inactivo o inexistente: 400. Documento fuera de 6 a 12 dígitos: 400. Inicio en el pasado: 400.

### GET `/api/lessons/mine`

Solo `INSTRUCTOR`. Sus clases, de la más próxima a la más lejana.

### POST `/api/lessons/{id}/cancel`

Solo `INSTRUCTOR`, y solo si la clase es suya y sigue `RESERVADA` y todavía no empieza.

Respuesta 200:

```json
{ "id": 0, "status": "CANCELADA" }
```

### GET `/api/reports/today`

Solo `INSTRUCTOR`.

```json
{ "date": "2026-11-20", "lessons": 2, "totalCop": 160000 }
```

`lessons` y `totalCop` ignoran las canceladas.

## Errores

Un manejador global deja todas las fallas con la misma forma.

```json
{ "mensaje": "texto concreto" }
```

Códigos: 400 validación o regla de datos, 401 sin token o token inválido, 403 rol incorrecto o clase ajena, 409 conflicto de horario, correo o placa.

## Cómo tiene que quedar el código

- Controladores finos. La regla de cruce vive en un servicio.
- Entidades de JPA separadas de los DTO que entran y salen.
- Repositorios de Spring Data.
- Validación con Bean Validation en los DTO.
- Contraseñas nunca se devuelven.
- `application.yml` lee la URL de Postgres, el usuario, la clave, el secreto JWT y el admin desde el entorno.

Paquetes sugeridos, no obligatorios: `auth`, `user`, `vehicle`, `lesson`, `report`, `error`.

## Pruebas mínimas

Cuatro alcanzan. Pueden ser de integración, con la base de test, o de servicio si el cruce queda aislado.

1. El login correcto devuelve un token. El login incorrecto devuelve 401.
2. Un instructor que intenta crear un vehículo recibe 403.
3. Dos clases del mismo instructor, 10:00 y 10:30, producen 409. Una a las 10:00 y otra a las 11:00 sí se crean.
4. El reporte de hoy no suma una clase cancelada.

## Para correrlo

`docker-compose.yml` levanta PostgreSQL 16. El README explica, en este orden:

1. Variables de entorno.
2. `docker compose up -d`
3. `./mvnw spring-boot:run`
4. Un login de ejemplo con curl, sin dejar una contraseña real pegada para producción.

Incluye una colección de Postman, o de Bruno, con las peticiones de este enunciado y el header `Authorization: Bearer`.

## Definición de terminado

La prueba está lista cuando otra persona clona el repositorio, sigue el README y logra reservar dos clases que no se cruzan, recibir 409 en un cruce, y ver el total del día.

En la hoja de vida, la línea puede decir:

> Ruta Norte. API de clases de conducción con Spring Boot, Spring Security, JWT y PostgreSQL. Un instructor y un vehículo no pueden tener dos clases en el mismo horario. Pruebas con JUnit.

Hasta que ese repositorio exista y arranque, esa línea no va en el CV.

## Orden para construirla

1. Proyecto en [start.spring.io](https://start.spring.io) con Java 17, Maven, Spring Web, Spring Security, Spring Data JPA, Validation y PostgreSQL Driver.
2. Docker Compose y una entidad `Vehicle` con su POST y su GET, todavía sin seguridad.
3. Login con JWT y las dos rutas protegidas por rol.
4. `Lesson` y la regla de cruce, con los mensajes de 409.
5. Cancelación y reporte del día, con la zona America/Bogota.
6. Las cuatro pruebas y el README.

El reporte y la colección de Postman van al final. No empieces por Kubernetes ni por un frontend.
