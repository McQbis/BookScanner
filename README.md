# BookScanner

## Description

This project aims to build a neural network model inspired by U-Net architecture to automatically straighten curved pages from books, making them appear as if scanned flat.

The system consists of:

- A mobile application for capturing images

- A server-side component for storing and processing images using AI

<!-- ## Image Processing Example -->

## Installation

To run the project locally:

```bash
git clone https://github.com/McQbis/BookScanner.git
cd BookScanner
```

### Server configuration

```bash
cd server
pip install -r requirements.txt
```
Create an ```.env``` file and provide the following environment variables:

```bash
# Secret key for Django – used for signing cookies, sessions, etc.
SECRET_KEY=
# Secret key to encryption keys of users
MASTER_KEY=
# Enables Django debug mode (only use True in development!)
DEBUG=True
# List of allowed domains/IPs that can access the app
ALLOWED_HOSTS=
# Domains allowed to make cross-origin requests (CORS)
CORS_ALLOWED_ORIGINS=

# Name of your PostgreSQL database
DB_NAME=
# Database username
DB_USER=
# Database password
DB_PASSWORD=
# Host address of your database
DB_HOST=
# Port your database is listening on (5432 is default for PostgreSQL)
DB_PORT=5432


# Should session cookies only be sent over HTTPS?
SESSION_COOKIE_SECURE=
# Should CSRF cookies only be sent over HTTPS?
CSRF_COOKIE_SECURE=
```

To access the Django admin panel, create a superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter a username, email, and password. Run another commands: 

```bash
python manage.py migrate
python manage.py collectstatic
```

Now you can run the server:

```bash
python manage.py runserver X.X.X.X:port
```

### Mobile application configuration

```bash
cd mobile_app/BookScanner
npm install
```

Create an ```.env``` file and provide the following environment variables:

```bash
EXPO_PUBLIC_API_BASE_URL=<server-address>/api
EXPO_PUBLIC_API_TIMEOUT=5000
```

Connect your Android device or run the emulator. And then launch the application:

```bash
npx expo run:android
```

### AI training module configuration

The folder ```server/ai_model/``` contains a module for training neural network models. You need to install libreoffice and poppler-utils.

```bash
apt install LibreOffice
apt-get install poppler-utils
```

Make sure you have already installed all the packages from the [requirements.txt](#server-configuration) file.

## Usage

### Server usage

### AI training module usage

## Technologies Used

This project is built using the following technologies and libraries:

### Frontend
- **React Native (Expo)** – for building the mobile application with a smooth cross-platform experience.
- **Axios** – for handling HTTP requests
- **Expo Secure Store** – for secure data storage

### Backend
- **Django** – high-level Python web framework for backend development.
- **Django REST Framework** – to build RESTful APIs.
- **Django REST Framework Simple JWT** – for JWT-based authentication.

### Database
- **psycopg2-binary** – PostgreSQL adapter for Python, used for database interactions.

### Python Libraries for Data Processing
- **PyTorch (torch)** – for machine learning and deep learning tasks.
- **NumPy** – for numerical computations.
- **OpenCV-python-headless** – computer vision tasks without GUI dependencies.
- **matplotlib** – for creating visualizations and plots.
- **pdf2image** – to convert PDF documents to images.
- **odfpy** – to read and write Open Document Format files.
- **cryptography** – for cryptographic operations and security.
- **python-decouple** – to manage environment variables and settings securely.

## Collaboration

This project is open to collaboration!  

If you're interested in contributing, improving features, or reporting issues, feel free to reach out.

You can contact me via open a **discussion in this repository**.
