# Organization Management Service

## Overview
This project implements a backend service for managing organizations in a multi-tenant architecture using FastAPI and MongoDB. Each organization receives its own dynamically created collection, while global metadata is stored in a master database. The system provides secure admin authentication via JWT and supports complete CRUD operations for organization management.

## Features

### Multi-Tenant Architecture
- Each organization is isolated using its own MongoDB collection:
  org_<organization_name>
- A master database stores all global organization metadata and admin credentials.

### Organization Management
- Create a new organization and associated admin.
- Fetch organization metadata.
- Update organization name and migrate existing data.
- Delete organization along with its associated collection.

### Admin Authentication
- Secure password hashing using Passlib.
- JWT-based authentication for protected operations.
- Only authorized admins can update or delete their organization.

### Technology Stack
- FastAPI
- MongoDB
- Uvicorn
- Pydantic
- Passlib
- Python 3.10+

## API Endpoints

### Create Organization  
POST /org/create  
Request Body:
{
  "organization_name": "example",
  "email": "admin@example.com",
  "password": "admin123"
}

### Get Organization  
GET /org/get?organization_name=<name>

### Update Organization  
PUT /org/update  
Request Body:
{
  "old_organization_name": "example",
  "new_organization_name": "example2",
  "email": "admin@example.com",
  "password": "admin123"
}

### Delete Organization  
DELETE /org/delete?organization_name=<name>

### Admin Login  
POST /admin/login  
Request Body:
{
  "email": "admin@example.com",
  "password": "admin123"
}  
Response:
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}

## Project Structure

Below is the full directory structure of the project:

org-management-service/  
│  
├── app/  
│   ├── main.py                 # FastAPI application entrypoint  
│   ├── config.py               # Environment and settings configuration  
│   ├── db.py                   # MongoDB connection and database helpers  
│   │  
│   ├── models/                 # Pydantic models and request/response schemas  
│   │   ├── organization.py  
│   │   └── admin.py  
│   │  
│   ├── routes/                 # Route handlers (API endpoints)  
│   │   ├── auth_routes.py  
│   │   └── org_routes.py  
│   │  
│   ├── core/                   # Security and authentication utilities  
│       ├── security.py         # Password hashing and JWT creation  
│       └── deps.py             # Authentication dependencies  
│  
├── requirements.txt            # Python dependencies  
├── .env                        # Environment variables (not committed to Git)  
└── README.md                   # Project documentation

## Installation and Setup

### 1. Clone the repository
git clone https://github.com/<your-username>/org-management-service.git  
cd org-management-service

### 2. Create and activate a virtual environment
python -m venv venv  
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Environment variables  
Create a `.env` file with the following:

MONGO_URI=mongodb://localhost:27017  
MASTER_DB_NAME=org_master  
JWT_SECRET=your_secret_key  
JWT_ALGORITHM=HS256  
ACCESS_TOKEN_EXPIRE_MINUTES=60

### 5. Start MongoDB (Windows)
net start MongoDB

### 6. Run the FastAPI server
uvicorn app.main:app --reload

### 7. Open API documentation
http://127.0.0.1:8000/docs

## Design Choices

- FastAPI offers high performance and clean routing structure.
- MongoDB enables dynamic collection creation suitable for multi-tenant systems.
- JWT authentication ensures stateless and secure admin operations.
- Passwords are securely hashed using Passlib.
- Multi-tenant architecture guarantees strong separation between organization data.

## Scalability and Trade-offs

### Advantages
- Strong tenant isolation with dedicated collections.
- Independent scaling and indexing for each organization.
- Cleaner access control per tenant.

### Trade-offs
- Large number of collections may increase operational overhead.
- Organization renaming requires full data migration.
- Requires careful indexing policies for high-volume tenants.

### Alternative Approach
A shared data model using a single collection with an `org_id` field can scale more easily to thousands of organizations, but reduces tenant isolation.

## Conclusion
This project meets all assignment requirements, implementing secure admin authentication, dynamic collection management, tenant isolation, and a clean modular architecture.
