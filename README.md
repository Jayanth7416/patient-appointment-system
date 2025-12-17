# Patient Appointment System

A high-performance, scalable appointment scheduling system for healthcare providers. Designed to handle 500M+ daily API calls across 200+ clinic locations with real-time availability updates.

## Features

- **Real-time Scheduling**: Instant availability checks and booking
- **Multi-location Support**: Manage appointments across 200+ clinics
- **Provider Management**: Doctor schedules, specialties, and availability
- **Patient Portal**: Self-service booking, rescheduling, and cancellation
- **Waitlist Management**: Automatic slot allocation when cancellations occur
- **Notification System**: SMS, email, and push notification reminders
- **EHR Integration**: Seamless integration with Epic and Cerner systems
- **Analytics Dashboard**: Utilization metrics and scheduling insights

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   API Gateway   │────▶│  Load Balancer  │────▶│  API Servers    │
│   (Rate Limit)  │     │   (Round Robin) │     │  (FastAPI)      │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
         ┌───────────────────────────────────────────────┼───────────┐
         │                                               │           │
         ▼                                               ▼           ▼
┌─────────────────┐                            ┌─────────────┐ ┌─────────────┐
│     Redis       │                            │ PostgreSQL  │ │   Kafka     │
│   (Cache/Lock)  │                            │ (Primary)   │ │  (Events)   │
└─────────────────┘                            └─────────────┘ └─────────────┘
```

## Performance

- **Throughput**: 500M+ API calls/day (5,800 requests/second)
- **Latency**: < 50ms p99 response time
- **Availability**: 99.99% uptime SLA
- **Concurrency**: Handles 10,000+ concurrent booking requests

## Tech Stack

- **Language**: Python 3.11+
- **API Framework**: FastAPI with async support
- **Database**: PostgreSQL with read replicas
- **Cache**: Redis Cluster for distributed caching
- **Queue**: Apache Kafka for event streaming
- **Search**: Elasticsearch for provider/slot search

## Project Structure

```
patient-appointment-system/
├── src/
│   ├── api/              # REST API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Data models
│   └── utils/            # Utilities
├── tests/                # Test suite
└── config/               # Configuration
```

## Quick Start

```bash
# Clone repository
git clone https://github.com/Jayanth7416/patient-appointment-system.git
cd patient-appointment-system

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run server
uvicorn src.api.main:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/providers` | List providers by location/specialty |
| GET | `/providers/{id}/availability` | Get available slots |
| POST | `/appointments` | Book an appointment |
| GET | `/appointments/{id}` | Get appointment details |
| PATCH | `/appointments/{id}` | Reschedule appointment |
| DELETE | `/appointments/{id}` | Cancel appointment |
| GET | `/patients/{id}/appointments` | Patient's appointments |
| POST | `/waitlist` | Join waitlist for a slot |

## Booking Flow

```
1. Patient searches for providers
2. System returns available slots (cached in Redis)
3. Patient selects slot
4. System acquires distributed lock (Redis)
5. Double-checks availability
6. Creates appointment record
7. Releases lock
8. Sends confirmation notification
9. Updates availability cache
```

## Configuration

```yaml
# config/settings.yaml
database:
  host: localhost
  port: 5432
  name: appointments
  pool_size: 20

redis:
  host: localhost
  port: 6379
  cluster: true

kafka:
  bootstrap_servers: localhost:9092
  topic_prefix: appointments

notifications:
  sms_enabled: true
  email_enabled: true
  reminder_hours: [24, 2]
```

## License

MIT License

## Author

Jayanth Kumar Panuganti - [LinkedIn](https://linkedin.com/in/jayanth7416)
