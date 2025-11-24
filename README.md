# CS-GradeCalculator

Sistema de cálculo de notas finales para docentes de UTEC, implementado con FastAPI, PostgreSQL y Docker, siguiendo principios de diseño orientado a objetos y clean code.

## Características

- **Registro de Evaluaciones**: Permite registrar notas y pesos (RF01).
- **Control de Asistencia**: Aplica penalizaciones si no se cumple el mínimo (RF02).
- **Puntos Extra**: Política configurable para otorgar puntos adicionales (RF03).
- **Cálculo Determinista**: Garantiza resultados consistentes (RF04, RNF03).
- **Alta Concurrencia**: Soporta múltiples solicitudes simultáneas (RNF02).
- **Calidad de Código**: Integración con SonarQube para análisis estático.

## Arquitectura y Diseño (UML)

El sistema sigue una arquitectura por capas con un dominio rico. A continuación se presenta el diagrama de clases:

```mermaid
classDiagram
    class Evaluation {
        +String name
        +Float score
        +Float weight
    }

    class Student {
        +String id
        +List~Evaluation~ evaluations
        +Boolean has_reached_minimum_classes
        +check_max_evaluations()
    }

    class GradeCalculationResult {
        +Float final_grade
        +Float average
        +Boolean penalty_applied
        +Boolean extra_points_applied
        +String details
    }

    class AttendancePolicy {
        +apply_penalty(grade: Float, has_reached_min: Boolean) Float
    }

    class ExtraPointsPolicy {
        +apply_extra(grade: Float, all_years_teachers: Boolean) Float
    }

    class GradeCalculator {
        -AttendancePolicy attendance_policy
        -ExtraPointsPolicy extra_policy
        +calculate(student: Student, all_years_teachers: Boolean) GradeCalculationResult
    }

    Student *-- "0..10" Evaluation : contains
    GradeCalculator ..> Student : uses
    GradeCalculator --> AttendancePolicy : uses
    GradeCalculator --> ExtraPointsPolicy : uses
    GradeCalculator ..> GradeCalculationResult : produces
```

## Requisitos Previos

- Docker y Docker Compose

## Instrucciones de Ejecución

1. **Clonar el repositorio**
2. **Iniciar los servicios**
   ```bash
   docker compose up -d --build
   ```
3. **Acceder a la API**
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
4. **Ejecutar Análisis de Calidad (SonarQube)**
   ```bash
   docker compose run --rm sonar-scanner
   ```

## Endpoints Principales

- `POST /students/{id}`: Crear estudiante.
- `POST /students/{id}/evaluations`: Agregar evaluación.
- `PUT /students/{id}/attendance`: Actualizar asistencia.
- `POST /calculate/{id}`: Calcular nota final.
