package com.zivastock.data.repository

import com.zivastock.data.local.database.dao.CountDao
import com.zivastock.data.local.database.entities.CountEntity
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CountRepository @Inject constructor(
    private val countDao: CountDao
) {
    
    suspend fun getCountById(id: Int): CountEntity? {
        return countDao.getCountById(id)
    }
    
    suspend fun getCountsBySessionAndSection(sessionId: Int, sectionId: Int): List<CountEntity> {
        return countDao.getCountsBySessionAndSection(sessionId, sectionId)
    }
    
    suspend fun insertCount(count: CountEntity) {
        countDao.insertCount(count)
    }
    
    suspend fun insertCounts(counts: List<CountEntity>) {
        countDao.insertCounts(counts)
    }
    
    suspend fun getUnsyncedCounts(): List<CountEntity> {
        return countDao.getUnsyncedCounts()
    }
    
    suspend fun markCountAsSynced(id: Int, syncedAt: String) {
        countDao.markCountAsSynced(id, syncedAt)
    }
    
    suspend fun deleteCount(id: Int) {
        countDao.deleteCount(id)
    }
}
