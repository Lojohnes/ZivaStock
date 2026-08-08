
package com.zivastock.di

import com.zivastock.data.repository.v2.*
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

// Repositories use constructor injection; this module may be used for interface bindings in the future.
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryV2Module {
    // TODO: add @Binds methods if interfaces are introduced
}
