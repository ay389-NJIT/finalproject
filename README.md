# Avinash Yalamanchi
# IS601 - Python Web API
-------------------------------------------------------------------------------------------------------------------------------
# Final Project - Calculator Web Application
- A web-based application calculator, built with FastAPI. It provides many different calculations: Add, Subtract, Multiplication, Division, Exponential, and Square Root. There is user authentication, profile management, and other additional features for ease of use. Automated testing, CI/CD pipelines, and containerized deployment via Docker are all present. 
-------------------------------------------------------------------------------------------------------------------------------
# Key Features
- **Authentication:** Secure JWT-based user registration and login with bcrypt password hashing
- **Operations:** Addition, Subtraction, Multiplication, Division, Exponential, Square Root
- **Statistics Dashboard:** Real-time analytics showing total calculations, most used operations, average operands, and visual breakdowns
- **Responsive UI:** Modern interface built with Tailwind CSS and vanilla JavaScript
- **RESTful API:** Complete backend API with interactive Swagger documentation
- **Docker Deployment:** Multi-container setup with PostgreSQL database
- **CI/CD Pipeline:** Automated testing and Docker Hub deployment via GitHub Actions
---
**Additional Features**
- **Expontential Capabilities:**
- Calculate base^exponent
- Support for positive exponents
- Support for zero exponent
- Support for negative exponents
- Support for fractional exponents
- Requires exactly two inputs
---
- **Square Root Capabilites:**
- Calculate square root of positive numbers
- Perfect squares
- Non-perfect squares
- Zero handling
- Decimal inputs
- Validates against negative inputs
- Requires exactly one input
---
**User Profile & Password Change:** 
- View current profile information
- Update username, email, first name, last name
- Change password with current password validation
- Input validation and error handling
---
**Calculation History:**
- Display count of all user calculations
- Track and display frequently used operation
- Calculate average number of inputs per calculation
- Visual progress bars showing distribution by type
- Automatically refresh after create/delete actions
- Statistics are user-specific and secure
-------------------------------------------------------------------------------------------------------------------------------
# Installation & Set-Up Instructions

1. **Clone Repository**
```bash
git clone https://github.com/ay389-NJIT/finalproject.git
cd finalproject
```

2. **Create Virtual Environment**
```bash
python3.12 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install playwright # python packages will be downloaded with requirements.txt, but all othere executables won't without this
```
4. **Create Repository in Docker**
- Manually created in either Docker Desktop or DockerHub Online.

5. **Generate Personal Token**
- Account Settings ->
- Personal Access Tokens ->
- Name Token ->
- Set to Read,Write,Delete

6. **Create Secrets in GitHub Repository**
- Repository Settings ->
- Secrets and Variables -> 
- Actions ->
- 2 New Repository Secrets -> 
- (1) DOCKERHUB_USERNAME = your DockerHub username
- (2) DOCKERHUB_TOKEN = generated R,W,D access token from DockerHub

7. **Start Application with Docker Compose**
```bash
docker-compose up --build
```

8. **Start Server**
```bash
uvicorn app.main:app --reload --port 8000
```

This will:
- Build the FastAPI application container
- Start PostgreSQL database container
- Initialize database tables automatically
- Expose application on http://localhost:8000
-------------------------------------------------------------------------------------------------------------------------------
# Local Testing Guide via Terminal

**All Tests (Unit + Integration):**
```bash
pytest tests/unit/ tests/integration/ -v
```

**Unit Tests Only:**
```bash
# All unit tests
pytest tests/unit/ -v
```

**Integration Tests Only:**
```bash
# All integration tests
pytest tests/integration/ -v
```

**End-to-End Tests:**

- Ensure server is active via: uvicorn app.main:app --reload --port 8000
- This should be in a seperate terminal from the main terminal you are using.
- For best results, split current terminal, access venv in the split terminal, and activate server.

```bash
# Run E2E tests in seperate terminal from uvicorn server terminal
pytest tests/e2e/ -v
```
-------------------------------------------------------------------------------------------------------------------------------
# Additional Links
- **Github Link:** https://github.com/ay389-NJIT/finalproject
- **DockerHub Link:** https://hub.docker.com/repository/docker/aviyalamnjit/finalproject/general