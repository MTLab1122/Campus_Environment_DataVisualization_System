# Campus Environment Data Visualization System — REST API Documentation

## 1. Overview and Standards

The Campus Environment REST API enables real-time environmental data ingestion from physical IoT sensor stations, programmatic access to historical time-series telemetry, alert management, and automated analytical reporting.

### Base URL
```
http://127.0.0.1:5000/api
```

### Protocol Standards
* **Data Format**: `application/json` for all request and response bodies.
* **Character Encoding**: UTF-8.
* **Timestamps**: ISO 8601 extended format (`YYYY-MM-DDTHH:MM:SSZ` or `YYYY-MM-DD HH:MM:SS`).
* **Authentication**: Session cookie or header-based authorization.

### Standard Response Envelope
All responses return a uniform JSON envelope:

#### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": { ... }
}
```

#### Error Response
```json
{
  "success": false,
  "message": "Human-readable explanation of error.",
  "errors": [ ... ]
}
```

---

## 2. Authentication Endpoints

### 2.1 User Login
* **Endpoint**: `POST /api/auth/login`
* **Access**: Public
* **Description**: Authenticate with username/email and password to establish an authorized session.

#### Request Body
```json
{
  "username": "admin",
  "password": "admin123"
}
```

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Login successful. Authenticated as admin (admin).",
  "data": {
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@campus.edu",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-10-18T14:43:06.123456"
    }
  }
}
```

#### Error Response (`401 Unauthorized`)
```json
{
  "success": false,
  "message": "Invalid credentials.",
  "errors": []
}
```

---

### 2.2 User Logout
* **Endpoint**: `POST /api/auth/logout`
* **Access**: Authenticated
* **Description**: Invalidate active session credentials.

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Logged out successfully.",
  "data": null
}
```

---

### 2.3 Current Session Profile
* **Endpoint**: `GET /api/auth/me`
* **Access**: Public / Authenticated
* **Description**: Query profile of current session user.

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Session active.",
  "data": {
    "authenticated": true,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@campus.edu",
      "role": "admin",
      "is_active": true
    }
  }
}
```

---

## 3. Campus Zones Endpoints

### 3.1 List Campus Zones
* **Endpoint**: `GET /api/zones`
* **Access**: Public
* **Description**: Retrieve all registered geographic campus zones.

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Retrieved 8 campus zones.",
  "data": [
    {
      "id": 1,
      "name": "Library",
      "code": "ZONE_LIB",
      "description": "Central academic study facility.",
      "location_details": "Building A, Floors 1-4",
      "sensor_count": 1,
      "created_at": "2026-10-18T14:43:06.200000"
    }
  ]
}
```

---

### 3.2 Create Campus Zone
* **Endpoint**: `POST /api/zones`
* **Access**: Admin Role Only
* **Description**: Provision a new physical monitoring zone.

#### Request Body
```json
{
  "name": "Innovation Hub",
  "code": "ZONE_INNOV",
  "description": "Robotics and computing lab complex.",
  "location_details": "Tech Quad Building E"
}
```

#### Response (`201 Created`)
```json
{
  "success": true,
  "message": "Campus zone created successfully.",
  "data": {
    "id": 9,
    "name": "Innovation Hub",
    "code": "ZONE_INNOV",
    "description": "Robotics and computing lab complex.",
    "location_details": "Tech Quad Building E",
    "created_at": "2026-10-18T14:45:00.000000"
  }
}
```

---

### 3.3 Get Zone Details
* **Endpoint**: `GET /api/zones/<id>`
* **Access**: Public
* **Description**: Retrieve specific zone attributes along with attached sensor hardware.

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": 1,
    "name": "Library",
    "code": "ZONE_LIB",
    "sensors": [
      {
        "id": 2,
        "sensor_code": "ENV-SN-LIB-01",
        "name": "Library Central Hall Environmental Node",
        "status": "online"
      }
    ]
  }
}
```

---

### 3.4 Update Campus Zone
* **Endpoint**: `PUT /api/zones/<id>`
* **Access**: Admin Role Only
* **Description**: Modify name, code, description, or location of an existing zone.

#### Request Body
```json
{
  "name": "Library Central Complex",
  "description": "Renovated study facility with modern acoustic insulation."
}
```

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Campus zone updated successfully.",
  "data": { ... }
}
```

---

### 3.5 Delete Campus Zone
* **Endpoint**: `DELETE /api/zones/<id>`
* **Access**: Admin Role Only
* **Description**: Remove zone and cascade deletion to associated sensors and readings.

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Campus zone 'Library' (ID 1) deleted successfully.",
  "data": null
}
```

---

## 4. Sensor Telemetry Station Endpoints

### 4.1 List Sensors
* **Endpoint**: `GET /api/sensors`
* **Query Parameters**:
  * `zone_id` (integer, optional)
  * `status` (string, optional: `online`, `offline`, `maintenance`)
* **Access**: Public

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Retrieved 8 sensor devices.",
  "data": [
    {
      "id": 1,
      "sensor_code": "ENV-SN-GATE-01",
      "zone_id": 1,
      "zone_name": "Main Gate",
      "zone_code": "ZONE_GATE",
      "name": "Main Gate Multi-Sensor Station",
      "model": "CampusSense-IoT-v2.1",
      "status": "online",
      "last_seen": "2026-10-18T14:43:00.000000"
    }
  ]
}
```

---

### 4.2 Provision New Sensor
* **Endpoint**: `POST /api/sensors`
* **Access**: Admin Role Only

#### Request Body
```json
{
  "sensor_code": "ENV-SN-LIB-02",
  "zone_id": 2,
  "name": "Library 3rd Floor Quiet Zone",
  "model": "AeroSense-Pro-Indoor",
  "status": "online"
}
```

#### Response (`201 Created`)
```json
{
  "success": true,
  "message": "Sensor provisioned successfully.",
  "data": {
    "id": 9,
    "sensor_code": "ENV-SN-LIB-02",
    "name": "Library 3rd Floor Quiet Zone",
    "status": "online"
  }
}
```

---

### 4.3 Update Sensor
* **Endpoint**: `PUT /api/sensors/<id>`
* **Access**: Admin Role Only

#### Request Body
```json
{
  "status": "maintenance"
}
```

---

### 4.4 Delete Sensor
* **Endpoint**: `DELETE /api/sensors/<id>`
* **Access**: Admin Role Only

---

## 5. Environmental Telemetry Readings Endpoints

### 5.1 Ingest Environmental Telemetry (IoT Hardware & Ingestion Pipeline)
* **Endpoint**: `POST /api/readings`
* **Access**: Public (IoT hardware stations)
* **Description**: Ingest telemetry packet. Calculates US EPA AQI automatically if omitted and triggers threshold evaluation.

#### Request Body
```json
{
  "sensor_code": "ENV-SN-LIB-01",
  "temperature": 23.4,
  "humidity": 48.2,
  "pm25": 14.5,
  "pm10": 26.0,
  "co2": 580.0,
  "noise": 36.8,
  "weather_condition": "Clear",
  "timestamp": "2026-10-18T14:00:00"
}
```

#### Response (`201 Created`)
```json
{
  "success": true,
  "message": "Environmental reading ingested successfully.",
  "data": {
    "reading": {
      "id": 1353,
      "sensor_code": "ENV-SN-LIB-01",
      "zone_name": "Library",
      "timestamp": "2026-10-18T14:00:00",
      "temperature": 23.4,
      "humidity": 48.2,
      "pm25": 14.5,
      "pm10": 26.0,
      "co2": 580.0,
      "noise": 36.8,
      "aqi": 56,
      "weather_condition": "Clear"
    },
    "alerts_triggered": []
  }
}
```

---

### 5.2 Query Telemetry Readings (With Filters)
* **Endpoint**: `GET /api/readings`
* **Query Parameters**:
  * `zone_id` (integer, optional)
  * `sensor_id` (integer, optional)
  * `start_date` (ISO date string, optional)
  * `end_date` (ISO date string, optional)
  * `limit` (integer, default: 100, max: 2000)
  * `page` (integer, default: 1)

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Retrieved 100 environmental readings.",
  "data": {
    "readings": [ ... ],
    "total_count": 1352,
    "page": 1,
    "limit": 100
  }
}
```

---

### 5.3 Latest Campus Readings
* **Endpoint**: `GET /api/readings/latest`
* **Access**: Public
* **Description**: Returns the latest reading across every campus zone.

---

## 6. Alerts & Thresholds Endpoints

### 6.1 Query System Alerts
* **Endpoint**: `GET /api/alerts`
* **Query Parameters**:
  * `zone_id` (integer, optional)
  * `is_resolved` (boolean, optional)
  * `severity` (string, optional: `Warning`, `Poor`, `Dangerous`)
  * `limit` (integer, default: 50)

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Retrieved 50 alerts.",
  "data": {
    "alerts": [
      {
        "id": 1,
        "parameter": "pm25",
        "measured_value": 58.2,
        "threshold_value": 55.0,
        "severity": "Dangerous",
        "message": "PM2.5 reached dangerous high level of 58.2 µg/m³ (Limit: >55.0 µg/m³)",
        "is_resolved": false,
        "created_at": "2026-10-18T12:00:00"
      }
    ],
    "statistics": {
      "total_active": 12,
      "dangerous": 2,
      "poor": 6,
      "warning": 4,
      "total_all_time": 253
    }
  }
}
```

---

### 6.2 Resolve Alert
* **Endpoint**: `PUT /api/alerts/<id>/resolve`
* **Access**: Public / Authenticated

---

### 6.3 List Threshold Boundaries
* **Endpoint**: `GET /api/alerts/thresholds`

---

### 6.4 Update Threshold Boundary
* **Endpoint**: `PUT /api/alerts/thresholds/<id>`
* **Access**: Admin Role Only

#### Request Body
```json
{
  "warning_max": 28.0,
  "poor_max": 38.0,
  "dangerous_max": 60.0
}
```

---

## 7. Reports & Dashboard Statistics

### 7.1 Consolidated Dashboard Statistics
* **Endpoint**: `GET /api/dashboard/stats`
* **Query Parameters**: `zone_id` (optional)
* **Description**: Supplies operational metrics, active alert tallies, and latest zone readings.

---

### 7.2 Period Summary Report
* **Endpoint**: `GET /api/reports/summary`
* **Query Parameters**:
  * `period`: `daily` | `weekly` | `monthly`
  * `zone_id`: integer (optional)

---

### 7.3 Telemetry CSV Export
* **Endpoint**: `GET /api/reports/export-csv`
* **Query Parameters**: `zone_id`, `start_date`, `end_date`
* **Response Header**: `Content-Type: text/csv`
* **Response**: Streamed CSV file download.

---

## 8. Environmental Health, Radar & Analytics Endpoints

### 8.1 Campus Environmental Health Index (CEHI)
* **Endpoint**: `GET /api/campus/health-index`
* **Access**: Public
* **Query Parameters**: `zone_id` (integer, optional)
* **Description**: Returns weighted CEHI score (0–100), letter grade (A+ to F), sub-index ratings (Air, Ventilation, Acoustics, Thermal), and automated safety recommendations.

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Retrieved Campus Environmental Health Index (CEHI) rating.",
  "data": {
    "score": 86.4,
    "grade": "A",
    "grade_label": "Very Good",
    "color": "#10B981",
    "sub_indices": {
      "air_quality": 89.2,
      "ventilation": 84.5,
      "acoustics": 85.0,
      "thermal_comfort": 87.0
    },
    "advisory": "High environmental quality with safe indoor and outdoor levels.",
    "zone_id": null
  }
}
```

---

### 8.2 Multi-Dimensional Zone Radar Matrix
* **Endpoint**: `GET /api/analytics/radar`
* **Access**: Public
* **Description**: Returns normalized 5-axis ratings (Air Cleanliness, Acoustic Quietness, IAQ Ventilation, Thermal Comfort, Particle Safety) for all 8 campus geographic zones.

#### Response (`200 OK`)
```json
{
  "success": true,
  "message": "Retrieved multi-dimensional zone radar comparison matrix.",
  "data": {
    "categories": [
      "Air Cleanliness",
      "Acoustic Quietness",
      "IAQ Ventilation",
      "Thermal Comfort",
      "Particle Safety"
    ],
    "zones": [
      {
        "zone_id": 1,
        "zone_name": "Main Gate",
        "zone_code": "ZONE_GATE",
        "values": [78.5, 62.0, 92.0, 84.0, 72.0]
      }
    ]
  }
}
```

---

### 8.3 Pairwise Parameter Correlations
* **Endpoint**: `GET /api/analytics/correlations`
* **Access**: Public
* **Description**: Computes Pearson correlation matrix between Temperature, Humidity, PM2.5, PM10, CO2, Noise, and AQI.

---

### 8.4 Simulate Instantaneous Telemetry Pulse
* **Endpoint**: `POST /api/readings/simulate-pulse`
* **Access**: Public / Authenticated
* **Request Body (JSON, Optional)**:
```json
{
  "zone_id": 2
}
```
* **Description**: Generates a realistic mock reading, saves to database, and triggers threshold alert evaluations.

---

### 8.5 Interactive Web Documentation Explorer
* **Endpoint**: `GET /api/docs`
* **Access**: Public
* **Description**: Serves the interactive, browser-based API testing console with 1-click live endpoint queries.

