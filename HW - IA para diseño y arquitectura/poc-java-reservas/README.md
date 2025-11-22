# ✅ Solución (POC en Java + Diagramas Mermaid)

## 1. Introducción
Este documento presenta el diseño conceptual y una prueba de concepto (POC) mínima de un sistema de reservación de habitaciones basado en microservicios. El objetivo es ilustrar la arquitectura, componentes clave, flujo de interacción durante una reserva y el ciclo de vida de una entidad `Reserva`.

Se implementa un POC en Java (Spring Boot) con servicios mínimos: `api-gateway`, `booking-service`, `inventory-service`, `payment-service`, `notification-service`, `auth-service`. Solo `booking-service` tiene lógica de dominio simplificada (gestión de reservas en memoria). Los demás servicios son esqueletos para representar separación de responsabilidades.

## 2. Diagrama de Arquitectura (Alto Nivel)
```mermaid
flowchart LR
  %% Capas
  subgraph Clients
    direction TB
    Web[Web SPA]
    Mobile[Mobile App]
  end

  subgraph Edge
    direction TB
    APIGW[API Gateway]
  end

  subgraph Services
    direction TB
    Auth[Auth Service]
    Booking[Booking Service]
    Inventory[Inventory Service]
    Payment[Payment Service]
    Notification[Notification Service]
    Search[Search Service]
  end

  subgraph Data
    direction TB
    PG[(PostgreSQL)]
    Redis[(Redis Cache)]
    MQ[(RabbitMQ)]
  end

  Web --> APIGW
  Mobile --> APIGW

  APIGW --> Auth
  APIGW --> Booking
  APIGW --> Inventory
  APIGW --> Payment
  APIGW --> Notification

  Booking --> Inventory
  Booking --> Payment
  Booking --> Notification

  Booking --> PG
  Inventory --> PG
  Payment --> PG

  Booking -- events --> MQ
  Payment -- events --> MQ
  Inventory -- events --> MQ
  MQ --> Notification

  Search --> Redis
  Booking --> Redis
```

## 3. Diagrama UML de Componentes
Representado como componentes y dependencias básicas.
```mermaid
classDiagram
   class APIGateway
   class AuthService
   class BookingService
   class InventoryService
   class PaymentService
   class NotificationService
   class SearchService
   class PostgreSQL
   class Redis
   class RabbitMQ

   <<Service>> APIGateway
   <<Service>> AuthService
   <<Service>> BookingService
   <<Service>> InventoryService
   <<Service>> PaymentService
   <<Service>> NotificationService
   <<Service>> SearchService
   <<Database>> PostgreSQL
   <<Cache>> Redis
   <<Broker>> RabbitMQ

   APIGateway --> AuthService : OAuth/JWT
   APIGateway --> BookingService : REST
   APIGateway --> InventoryService : REST
   APIGateway --> PaymentService : REST
   APIGateway --> NotificationService : REST
   BookingService --> InventoryService : Disponibilidad
   BookingService --> PaymentService : Cobro
   BookingService --> NotificationService : Confirmación
   BookingService --> PostgreSQL : Persistencia
   InventoryService --> PostgreSQL : Stock habitaciones
   PaymentService --> PostgreSQL : Transacciones
   SearchService --> Redis : Índices/búsquedas
   BookingService --> RabbitMQ : Emite eventos
   PaymentService --> RabbitMQ : Emite eventos
   NotificationService --> RabbitMQ : Consume eventos
```

## 4. Diagrama de Secuencia (Proceso de Reserva)
```mermaid
sequenceDiagram
      actor Usuario
      participant Web as Frontend
      participant APIGW as API Gateway
      participant BOOK as Booking Service
      participant INV as Inventory Service
      participant PAY as Payment Service
      participant NOTIF as Notification Service

      Usuario->>Web: Buscar habitación
      Web->>APIGW: GET /rooms?fecha
      APIGW->>INV: Consultar disponibilidad
      INV-->>APIGW: Lista habitaciones
      APIGW-->>Web: Respuesta
      Usuario->>Web: Selecciona habitación y reserva
      Web->>APIGW: POST /booking
      APIGW->>BOOK: Crear reserva (NEW)
      BOOK->>INV: Bloquear habitación temporal
      INV-->>BOOK: OK
      BOOK->>PAY: Iniciar pago
      PAY-->>BOOK: Pago aprobado
      BOOK->>NOTIF: Emitir evento confirmación
      NOTIF-->>Usuario: Email / Push Confirmación
      BOOK-->>APIGW: Reserva CONFIRMED
      APIGW-->>Web: Respuesta final
```

## 5. Diagrama de Estado (Reserva)
```mermaid
stateDiagram-v2
      [*] --> NEW
      NEW --> PENDING_PAYMENT : Solicitud creada
      PENDING_PAYMENT --> CONFIRMED : Pago OK
      PENDING_PAYMENT --> CANCELLED : Pago fallido / timeout
      CONFIRMED --> CHECKED_IN : Usuario se registra
      CHECKED_IN --> COMPLETED : Checkout
      CONFIRMED --> CANCELLED : Cancelación usuario
      NEW --> EXPIRED : No avanza (timeout hold)
      PENDING_PAYMENT --> EXPIRED : Tiempo excedido
      CANCELLED --> [*]
      COMPLETED --> [*]
      EXPIRED --> [*]
```

## 6. Capturas UI (Estructura)

[Link to the designs](https://app.uizard.io/p/a1b4f285)

### UI Screenshots

![Landing](./Landing.png)
![Sign in page](./Sign%20in%20page.png)
![Room search](./Room%20search.png)
![Room details](./Room%20details.png)
![Booking confirmation](./Booking%20confirmation.png)

## 7. Tecnologías y Justificación
- **Spring Boot**: Rapidez para exponer REST y empaquetar microservicios independientes.
- **API Gateway**: Punto único de entrada (seguridad, routing, rate limiting futuro).
- **Separación de servicios**: Facilita escalado independiente y aislar responsabilidades.