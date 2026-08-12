
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.SecondCountEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface SecondCountDao {
    @Query("SELECT * FROM v2_second_counts")
    fun getAll(): Flow<List<SecondCountEntity>>

    @Query("SELECT * FROM v2_second_counts WHERE isSynced = 0")
    fun getUnsynced(): Flow<List<SecondCountEntity>>

    @Query("SELECT * FROM v2_second_counts WHERE sessionId = :sessionId")
    fun getBySession(sessionId: Long): Flow<List<SecondCountEntity>>

    @Query("SELECT * FROM v2_second_counts WHERE id = :id")
    suspend fun getById(id: Long): SecondCountEntity?

    @Query("SELECT * FROM v2_second_counts WHERE sessionId = :sessionId AND productId = :productId AND userId = :userId AND ((fileNumber = :fileNumber) OR (fileNumber IS NULL AND :fileNumber IS NULL)) AND ((sectionNumber = :sectionNumber) OR (sectionNumber IS NULL AND :sectionNumber IS NULL)) LIMIT 1")
    suspend fun findByScope(sessionId: Long, productId: Long, userId: Long, fileNumber: String?, sectionNumber: String?): SecondCountEntity?

    @Query("UPDATE v2_second_counts SET isSynced = 1, syncedAt = :syncedAt WHERE id = :id")
    suspend fun markAsSynced(id: Long, syncedAt: String)


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: SecondCountEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<SecondCountEntity>): List<Long>

    @Update
    suspend fun update(item: SecondCountEntity)

    @Delete
    suspend fun delete(item: SecondCountEntity)

    @Query("DELETE FROM v2_second_counts")
    suspend fun deleteAll()
}
