# ZivaStock Android App

Kotlin Android app for stock counting, barcode scanning, and background synchronization.

## Features

- Login with JWT authentication
- Barcode scanning with CameraX and ML Kit
- Offline count saving with Room database
- Background sync with WorkManager
- Sync status monitoring
- Hilt dependency injection

## Tech Stack

- Kotlin
- Android SDK 34 (compileSdk), minSdk 26
- Hilt 2.48
- Room 2.6.1
- WorkManager 2.9.0
- Retrofit 2.9.0
- CameraX 1.3.1
- ML Kit Barcode Scanning

## Getting Started

1. Open the `android-app` folder in Android Studio
2. Sync project with Gradle files
3. Build and run on an emulator or device

## Project Structure

```
android-app/
├── app/
│   ├── src/main/java/com/zivastock/
│   │   ├── ZivaStockApplication.kt
│   │   ├── data/
│   │   │   ├── local/      # Room database, DAOs, entities, DataStore
│   │   │   ├── remote/     # Retrofit API service and DTOs
│   │   │   └── repository/ # Repository classes
│   │   ├── di/             # Hilt modules
│   │   ├── presentation/   # Activities and ViewModels
│   │   ├── sync/           # SyncWorker and SyncScheduler
│   │   └── utils/          # Network utilities
│   └── src/main/res/       # Layouts, drawables, values, menus
├── build.gradle.kts        # Project-level build file
├── settings.gradle.kts
└── gradle.properties
```

## Backend URL

The default API URL is the deployed Render API:

```text
https://zivastock-api.onrender.com/api/v1/
```

For local emulator development, override it during the build:

```powershell
.\gradlew.bat assembleDebug -PapiBaseUrl=http://10.0.2.2:8000/api/v1/
```

For a physical device, use a reachable HTTPS server or the computer LAN address.
The API base URL can be overridden without changing source code using `-PapiBaseUrl`.
