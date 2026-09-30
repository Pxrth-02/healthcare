# Healthcare Management System

## 1. Project Overview
The Healthcare Management System is a clinical administration platform providing dual-layer access: a session-authenticated browser interface and a JWT-authenticated RESTful API. The system manages three core healthcare domains:
- Patients: Strictly isolated per user account.
- Doctors: A shared clinical directory readable across all authenticated staff, with write permissions restricted strictly to the record creator.
- Patient-Doctor Mappings: Associations between a user's patient and any clinical doctor, preventing duplicate assignments and enforcing owner-scoped access.

---

## 2. Technology Stack
- Backend Framework: Django 5.x
- REST Framework: Django REST Framework (DRF) 3.15+
- Token Authentication: djangorestframework-simplejwt
- Configuration Management: python-decouple
- Database Engine: PostgreSQL 16+ via psycopg2-binary
- Production Server: Gunicorn (WSGI HTTP Server)
- Static File Handling: WhiteNoise (with compression)
- Database URL Parser: dj-database-url
- Frontend: Django Templates, Vanilla HTML5, Custom CSS
- Typography: Open Sans (Google Fonts)
- Color Palette: Deep Forest Green (#044511) and Soft Sage Green (#C8D6B8)

---

## 3. Local Setup
1. Clone or extract the repository into your local directory:
   ```bash
   cd healthcare
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # Linux/macOS:
   source venv/bin/activate
   ```

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (see Section 5):
   Copy `.env.example` to `.env` and provide your local credentials.

---

## 4. PostgreSQL Database and User Creation
Run the following SQL commands using the PostgreSQL CLI (psql) or your PostgreSQL administration tool:

```sql
CREATE DATABASE healthcare_db;
CREATE USER healthcare_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO healthcare_user;
ALTER DATABASE healthcare_db OWNER TO healthcare_user;
GRANT ALL ON SCHEMA public TO healthcare_user;

-- Optional: To allow Django to create test databases during standard PostgreSQL testing:
ALTER USER healthcare_user CREATEDB;
```

---

## 5. Environment Variables
Create a `.env` file in the root project directory containing the following variables:

```ini
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
DB_NAME=healthcare_db
DB_USER=healthcare_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 6. Migration Commands
Apply all existing database migrations:
```bash
python manage.py migrate
```

Verify that no unapplied model changes remain:
```bash
python manage.py makemigrations --check
```

---

## 7. How to Create Superuser
Create an administrative superuser account for accessing the Django Admin interface (`/admin/`):
```bash
python manage.py createsuperuser
```

Prompts:
- Email: `admin@healthcare.local`
- Name: `Administrator`
- Password: `[secure password]`
- Password (again): `[secure password]`

---

## 8. How to Run Server
Start the development server:
```bash
python manage.py runserver
```

The application will be accessible at:
- Web Application: http://127.0.0.1:8000/
- Admin Portal: http://127.0.0.1:8000/admin/
- API Root: http://127.0.0.1:8000/api/

### Production Deployment on Render
1. Create a new PostgreSQL Database on Render:
   - Go to Render Dashboard -> New -> PostgreSQL.
   - Note the Internal Database URL (or connection details).

2. Create a new Web Service on Render:
   - Go to Render Dashboard -> New -> Web Service.
   - Connect your GitHub repository.
   - Environment: Python 3
   - Build Command: `./build.sh`
   - Start Command: `gunicorn config.wsgi:application`

3. Configure Environment Variables in Render Dashboard:
   - `SECRET_KEY`: Set to a strong random production key.
   - `DEBUG`: `False`
   - `DATABASE_URL`: Set to the Internal Database URL from step 1.
   - `ALLOWED_HOSTS`: `localhost,127.0.0.1` (Render automatically appends your `.onrender.com` domain via `RENDER_EXTERNAL_HOSTNAME`).

---

## 9. API Endpoints

### Authentication Endpoints (Public)
| Method | Endpoint | Description | Payload | Status Codes |
|---|---|---|---|---|
| POST | `/api/auth/register/` | Register user | `{"name", "email", "password"}` | 201 Created, 400 Bad Request |
| POST | `/api/auth/login/` | Authenticate and obtain JWT | `{"email", "password"}` | 200 OK, 401 Unauthorized |

### Patient Endpoints (JWT Required)
| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| GET | `/api/patients/` | List current user patients | 200 OK, 401 Unauthorized |
| POST | `/api/patients/` | Create patient | 201 Created, 400 Bad Request, 401 Unauthorized |
| GET | `/api/patients/<id>/` | Retrieve patient details | 200 OK, 401 Unauthorized, 404 Not Found |
| PUT | `/api/patients/<id>/` | Update patient record | 200 OK, 400 Bad Request, 401 Unauthorized, 404 Not Found |
| DELETE | `/api/patients/<id>/` | Delete patient record | 204 No Content, 401 Unauthorized, 404 Not Found |

### Doctor Endpoints (JWT Required)
| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| GET | `/api/doctors/` | List all doctors (global read) | 200 OK, 401 Unauthorized |
| POST | `/api/doctors/` | Create doctor record | 201 Created, 400 Bad Request, 401 Unauthorized |
| GET | `/api/doctors/<id>/` | Retrieve doctor record | 200 OK, 401 Unauthorized, 404 Not Found |
| PUT | `/api/doctors/<id>/` | Update doctor record (creator only) | 200 OK, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found |
| DELETE | `/api/doctors/<id>/` | Delete doctor record (creator only) | 204 No Content, 401 Unauthorized, 403 Forbidden, 404 Not Found |

### Patient-Doctor Mapping Endpoints (JWT Required)
| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| GET | `/api/mappings/` | List mappings for current user patients | 200 OK, 401 Unauthorized |
| POST | `/api/mappings/` | Assign doctor to patient | 201 Created, 400 Bad Request, 401 Unauthorized |
| GET | `/api/mappings/<pk>/` | List mappings for patient_id=`<pk>` | 200 OK, 401 Unauthorized, 404 Not Found |
| DELETE | `/api/mappings/<pk>/` | Delete mapping with mapping_id=`<pk>` | 204 No Content, 401 Unauthorized, 404 Not Found |

---

## 10. Authentication Instructions for Postman
1. Open Postman and create a new request or collection.
2. Send a POST request to:
   - URL: `http://127.0.0.1:8000/api/auth/login/`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```json
     {
         "email": "user@example.com",
         "password": "your_password"
     }
     ```
3. Copy the `access` value from the JSON response:
   ```json
   {
       "access": "eyJhbGciOiJIUzI1NiIsIn...",
       "refresh": "eyJhbGciOiJIUzI1NiIsIn..."
   }
   ```
4. On subsequent requests to protected endpoints (`/api/patients/`, `/api/doctors/`, `/api/mappings/`):
   - Under the Authorization tab, set Type to Bearer Token.
   - Paste the access token into the Token field.
   - Alternatively, add a request header manually:
     `Authorization: Bearer <your_access_token>`
5. Access tokens expire after 1 hour. Refresh tokens expire after 24 hours.

---

## 11. Patient Ownership Rules
- Strict user-level data isolation is enforced at the database queryset level.
- When creating a patient (`POST /api/patients/` or `/patients/create/`), `created_by` is assigned automatically to `request.user`. Clients cannot supply or override this field.
- `GET /api/patients/` returns only patients created by the authenticated user.
- Detail, Update, and Delete endpoints (`/api/patients/<id>/`) filter by `created_by=request.user`.
- Attempting to access, modify, or delete a patient owned by another user returns HTTP 404 Not Found (never 403), preventing attackers from enumerating or verifying the existence of IDs.

---

## 12. Doctor Creator-Only Write Rule
- The doctor directory is a shared clinical catalog readable by all authenticated staff.
- Any authenticated user can view the full list (`GET /api/doctors/`) or view any doctor profile (`GET /api/doctors/<id>/`).
- When a doctor is created, `created_by` is assigned to `request.user`.
- Updates (`PUT /api/doctors/<id>/`) and Deletions (`DELETE /api/doctors/<id>/`) are restricted to the user who created the record via the DRF object permission class `IsCreatorOrReadOnly`.
- If a user attempts to edit or delete a doctor created by someone else, the API returns HTTP 403 Forbidden.
- In the browser UI (`/doctors/`), Edit and Delete action buttons are only rendered for doctors created by the logged-in user; other records display a "Read Only" badge.

---

## 13. Mapping Ownership Rule
- A patient-doctor mapping associates a patient with a doctor.
- The patient must belong to the authenticated user (`created_by=request.user`). Attempting to map another user's patient returns HTTP 400 Bad Request.
- The doctor may be any registered doctor in the system, regardless of creator.
- `GET /api/mappings/` returns only mappings where `mapping.patient.created_by == request.user`.
- Deleting a mapping requires that `mapping.patient.created_by == request.user`; otherwise, HTTP 404 Not Found is returned.

---

## 14. Duplicate Mapping Behaviour
- A patient cannot be assigned to the same doctor more than once.
- Enforced at the model level via a UniqueConstraint on fields `["patient", "doctor"]`.
- Enforced at serializer and form levels via validation:
  Attempting to create a duplicate assignment returns HTTP 400 Bad Request with:
  ```json
  {"non_field_errors": ["This doctor is already assigned to this patient."]}
  ```
- In the browser UI (`/patients/<id>/mappings/`), submitting an existing assignment triggers an inline form error alert without creating a duplicate record.

---

## 15. The GET-vs-DELETE Mapping URL Quirk Explained Clearly
The endpoint pattern `/api/mappings/<int:pk>/` serves two distinct semantic operations depending on the HTTP method:

1. `GET /api/mappings/<int:pk>/`
   - The `pk` parameter represents `patient_id`.
   - It retrieves all active doctor assignments for that specific patient.
   - Permission rule: The patient must belong to `request.user`. If not found or owned by another user, the view returns HTTP 404 Not Found.
   - Response: JSON list of doctor assignments for that patient (HTTP 200 OK).

2. `DELETE /api/mappings/<int:pk>/`
   - The `pk` parameter represents `mapping_id`.
   - It deletes the single assignment record whose primary key is `pk`.
   - Permission rule: The associated patient must belong to `request.user`. If the mapping does not exist or its patient belongs to another user, the view returns HTTP 404 Not Found.
   - Response: Empty body with HTTP 204 No Content.

This dual-semantic pattern is handled explicitly by `MappingSharedDetailView` in `mappings/views.py`.

---

## 16. Browser UI Routes and Screens

### Authentication Views
- `/` (Root): Redirects unauthenticated users to `/login/` and authenticated users to `/patients/`.
- `/login/`: Clean authentication card with email and password fields. Redirects to `/patients/` upon success.
- `/register/`: Registration card with name, email, password, and confirmation password fields. Validates case-insensitive unique email and password requirements.
- `/logout/`: Terminates active session and redirects to `/login/`.

### Patient Management
- `/patients/`: Tabular roster of user-scoped patients (columns: Name, Email, Age, Gender, Phone, Actions). Actions include Edit, Manage Doctors, and Delete.
- `/patients/create/`: Form for adding a new patient (name, email, age, gender, phone).
- `/patients/<id>/edit/`: Form for updating an existing patient record. Scoped strictly to the owner.
- `/patients/<id>/delete/`: Confirmation prompt showing patient summary before permanent deletion.

### Doctor Directory
- `/doctors/`: Shared directory of all doctors. Displays Name, Specialization badge, Experience, Contact info, and Creator email. Shows Edit/Delete buttons for records owned by the current user, or a "Read Only" badge for others.
- `/doctors/create/`: Form for registering a new doctor (name, specialization, experience_years, age, gender, phone).
- `/doctors/<id>/edit/`: Form for updating doctor details. Non-creators attempting direct access receive HTTP 403 Forbidden.
- `/doctors/<id>/delete/`: Confirmation prompt for doctor deletion. Non-creators receive HTTP 403 Forbidden.

### Patient-Doctor Mappings
- `/mappings/`: Overview listing all doctor assignments across all patients owned by the current user. Columns: Patient Name, Assigned Doctor, Specialization, Assigned Date, Actions (Remove).
- `/patients/<id>/mappings/`: Dedicated assignment screen for a specific patient. Displays patient summary header, a dropdown to assign any available doctor, and a list of currently assigned doctors with Remove buttons.
- `/mappings/<id>/delete/`: Confirmation prompt before deleting a mapping assignment.

---

## 17. Known Intentional Decisions
1. Dual-Semantic Mapping URL:
   `/api/mappings/<pk>/` uses `pk` as `patient_id` for GET and `mapping_id` for DELETE to adhere strictly to the project specification without introducing separate endpoints.
2. 404 vs 403 Status Code Semantics:
   - Patients and Mappings return 404 Not Found when accessed by non-owners. This avoids leaking the existence of sensitive patient IDs to unauthorized callers.
   - Doctors return 403 Forbidden on unauthorized writes (PUT/DELETE) because doctor records are public within the clinic directory, so existence enumeration is not a privacy issue.
3. Creator Scoping via Model Save:
   Serializer and form fields for `created_by` are strictly read-only. `created_by` is assigned server-side from `request.user` during `perform_create` or `form.save(commit=False)`.
4. Dual Authentication Systems:
   - Browser UI utilizes Django session cookies with standard CSRF protection and `LoginRequiredMixin`.
   - REST API utilizes Stateless JWT Bearer tokens via `djangorestframework-simplejwt`.
5. In-Memory / SQLite Test Optimization:
   When running `python manage.py test`, Django automatically switches to an in-memory SQLite database and fast MD5 password hashers. This ensures tests run in ~1 second and avoids requiring PostgreSQL CREATEDB superuser permissions.
6. Pure Vanilla CSS Design System:
   No heavyweight external CSS frameworks. Styled using modern CSS variables, Open Sans typography, and clean `#044511` / `#C8D6B8` clinical green tones.

---

## 18. Testing Checklist
The test suite covers unit, integration, and security verification across all four apps.

### System Verification Commands
- Check system configuration:
  ```bash
  python manage.py check
  ```
  Expected: System check identified no issues (0 silenced).

- Check pending migrations:
  ```bash
  python manage.py makemigrations --check
  ```
  Expected: No changes detected.

- Run full test suite:
  ```bash
  python manage.py test
  ```
  Expected: 19 tests run with 0 failures, 0 errors.

### Acceptance Criteria Matrix
- [x] Auth: Register user via API (201)
- [x] Auth: Reject duplicate email registration (400)
- [x] Auth: Login and receive JWT access/refresh tokens (200)
- [x] Auth: Reject invalid credentials (401)
- [x] Auth: Reject unauthenticated API requests (401)
- [x] Patients: Create patient automatically assigned to current user (201)
- [x] Patients: List patients scoped strictly to current user (200)
- [x] Patients: Detail own patient (200)
- [x] Patients: Cross-user detail returns 404 Not Found
- [x] Patients: Cross-user update returns 404 Not Found
- [x] Patients: Cross-user delete returns 404 Not Found
- [x] Patients: Update own patient (200)
- [x] Patients: Reject invalid age > 150 (400)
- [x] Patients: Reject invalid gender (400)
- [x] Doctors: Create doctor assigned to current user (201)
- [x] Doctors: Global read of all doctors for any authenticated user (200)
- [x] Doctors: Global read of doctor detail (200)
- [x] Doctors: Non-creator update returns 403 Forbidden
- [x] Doctors: Non-creator delete returns 403 Forbidden
- [x] Doctors: Creator can update doctor (200)
- [x] Doctors: Creator can delete doctor (204)
- [x] Mappings: Assign own patient to own doctor (201)
- [x] Mappings: Assign own patient to another user doctor (201)
- [x] Mappings: Reject assignment of other user patient (400)
- [x] Mappings: Reject duplicate assignment of same patient and doctor (400)
- [x] Mappings: Reject assignment with non-existent doctor (400)
- [x] Mappings: List mappings scoped to current user patients (200)
- [x] Mappings: GET /api/mappings/<patient_id>/ returns patient assignments (200)
- [x] Mappings: GET /api/mappings/<patient_id>/ for other patient returns 404
- [x] Mappings: DELETE /api/mappings/<mapping_id>/ by non-owner returns 404
- [x] Mappings: DELETE /api/mappings/<mapping_id>/ by owner deletes assignment (204)
- [x] Cascades: Deleting a patient deletes all related mappings
- [x] Cascades: Deleting a doctor deletes all related mappings
- [x] UI: Root redirects to /login/
- [x] UI: Protected routes redirect unauthenticated users to /login/
- [x] UI: Patient and Doctor forms validate age bounds and required fields
- [x] UI: Doctor listing displays Read Only badge for non-owned doctors
- [x] UI: CSS utilizes Open Sans, #044511, and #C8D6B8 with zero emojis or oversized cards
