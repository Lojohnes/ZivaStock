# ProGuard rules for ZivaStock

# Keep model classes used by Gson/Retrofit
-keep class com.zivastock.data.remote.dto.** { *; }

# Keep Room entities
-keep class com.zivastock.data.local.database.entities.** { *; }

# Keep Hilt generated classes
-keep class dagger.hilt.** { *; }
-keep class * extends dagger.hilt.internal.GeneratedComponentManagerAccessor { *; }

# Keep WorkManager workers
-keep class * extends androidx.work.Worker { *; }
-keep class * extends androidx.work.CoroutineWorker { *; }
