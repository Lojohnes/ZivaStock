package com.zivastock.sync

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object ConflictResolver {

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())

    enum class Resolution {
        USE_LOCAL,
        USE_REMOTE,
        MERGE
    }

    fun resolve(localTimestamp: String?, remoteTimestamp: String?): Resolution {
        val localDate = parse(localTimestamp) ?: Date(0)
        val remoteDate = parse(remoteTimestamp) ?: Date(0)

        return when {
            remoteDate.after(localDate) -> Resolution.USE_REMOTE
            localDate.after(remoteDate) -> Resolution.USE_LOCAL
            else -> Resolution.USE_LOCAL // last writer with equal timestamp wins
        }
    }

    private fun parse(value: String?): Date? {
        return try {
            value?.let { dateFormat.parse(it) }
        } catch (e: Exception) {
            null
        }
    }
}
