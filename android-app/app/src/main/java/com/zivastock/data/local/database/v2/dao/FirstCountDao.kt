
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.FirstCountEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface FirstCountDao {
    @Query("SELECT * FROM v2_first_counts")
    fun getAll(): Flow<List<FirstCountEntity>>

    @Query("SELECT * FROM v2_first_counts WHERE isSynced = 0")
    fun getUnsynced(): Flow<List<FirstCountEntity>>

    @Query("SELECT * FROM v2_first_counts WHERE sessionId = :sessionId")
    fun getBySession(sessionId: Long): Flow<List<FirstCountEntity>>

    @Query("SELECT * FROM v2_first_counts WHERE id = :id")
    suspend fun getById(id: Long): FirstCountEntity?

    @Query("SELECT * FROM v2_first_counts WHERE sessionId = :sessionId AND productId = :productId AND userId = :userId AND ((fileNumber = :fileNumber) OR (fileNumber IS NULL AND :fileNumber IS NULL)) AND ((sectionNumber = :sectionNumber) OR (sectionNumber IS NULL AND :sectionNumber IS NULL)) LIMIT 1")
    suspend fun findByScope(sessionId: Long, productId: Long, userId: Long, fileNumber: String?, sectionNumber: String?): FirstCountEntity?

    @Query("UPDATE v2_first_counts SET isSynced = 1, syncedAt = :syncedAt WHERE id = :id")
    suspend fun markAsSynced(id: Long, syncedAt: String)


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: FirstCountEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<FirstCountEntity>): List<Long>

    @Update
    suspend fun update(item: FirstCountEntity)

    @Delete
    suspend fun delete(item: FirstCountEntity)

    @Query("DELETE FROM v2_first_counts")
    suspend fun deleteAll()
}
