
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.SessionAssignmentEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface SessionAssignmentDao {
    @Query("SELECT * FROM v2_session_assignments")
    fun getAll(): Flow<List<SessionAssignmentEntity>>


    @Query("SELECT * FROM v2_session_assignments WHERE id = :id")
    suspend fun getById(id: Long): SessionAssignmentEntity?


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: SessionAssignmentEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<SessionAssignmentEntity>): List<Long>

    @Update
    suspend fun update(item: SessionAssignmentEntity)

    @Delete
    suspend fun delete(item: SessionAssignmentEntity)

    @Query("DELETE FROM v2_session_assignments")
    suspend fun deleteAll()
}
