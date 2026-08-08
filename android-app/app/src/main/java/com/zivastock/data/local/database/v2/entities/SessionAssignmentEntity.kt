
        package com.zivastock.data.local.database.v2.entities

        import androidx.room.Entity
import androidx.room.PrimaryKey

        @Entity(tableName = "v2_session_assignments")
        data class SessionAssignmentEntity(
            @PrimaryKey
    val id: Long = 0,
        val sessionId: Long = 0,
    val userId: Long = 0,
    val shelfSectionId: Long? = null,
    val assignmentRole: String = "first_counter",
    val status: String = "assigned",
    val assignedBy: Long? = null,
    val assignedAt: String? = null,
    val startedAt: String? = null,
    val completedAt: String? = null,
        )
