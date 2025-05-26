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
# Port your database is listening on (5432 is the default for PostgreSQL)
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

Follow the prompts to enter a username, email, and password. Run other commands: 

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
apt install libreoffice
apt-get install poppler-utils
```

Make sure you have already installed all the packages from the [requirements.txt](#server-configuration) file.

## Usage

### Server usage

The admin site can be found at ```<server-address>/zone_51_hehhe/```.

The server stores users' encrypted photos, where each user has their encrypted key used to encrypt their photos. The keys are encrypted using the ```MASTER_KEY``` in your ```.env``` file. Photos and user keys are in the ```media/``` folder.

#### The application exposes two endpoints for retrieving decrypted user photos:

**1. Authenticated Photo Access** 
```http
GET /api/photos/view/<photo_id>/
```

- Requires user authentication (JWT or session-based)

- Decrypts the image server-side and returns it as a FileResponse

- Suitable for internal tools, admin panels, or secure web apps

- **WARNING**: Not ideal for React Native or similar environments where images are embedded via URI

**Response:**

**- 200** OK with decrypted image content

**- 404** Not Found if photo doesn’t exist or decryption fails

**2. Temporary Signed URL**
```http
GET /api/photos/temp-view/<signed_value>/**
```

- Does not require authentication

- The signed_value is a time-limited, cryptographically signed token that maps to a specific photo

- Designed for mobile applications (e.g. React Native) where images are embedded via direct URIs

- Safer and more efficient for frontend usage

```jsx
<Image source={{ uri: '<server-addreess>/api/photos/temp-view/abc123xyz/' }} />
```

**Response:**

***- 200*** OK with decrypted image content

***- 403*** Forbidden if the link is invalid or expired

***- 404*** Not Found if the photo does not exist

### AI training module usage

## Technologies Used

This project is built using the following technologies and libraries:

### Frontend
- **React Native (Expo)** – for building the mobile application
- **Axios** – for handling HTTP requests
- **Expo Secure Store** – for secure data storage

### Backend
- **Django** – a high-level Python web framework for backend development.
- **Django REST Framework** – to build RESTful APIs.
- **Django REST Framework Simple JWT** – for JWT-based authentication.

### Database
- **PostgreSQL**

### Python Libraries for Data Processing
- **PyTorch** – for machine learning and deep learning tasks.
- **OpenCV-python-headless** – computer vision tasks without GUI dependencies.
- **matplotlib** – for creating visualizations and plots.
- **cryptography** – for cryptographic operations and security.

## Collaboration

This project is open to collaboration!  

If you're interested in contributing, improving features, or reporting issues, feel free to reach out.

You can contact me by opening a **discussion in this repository**.
