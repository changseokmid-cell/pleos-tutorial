plugins {
    id("com.android.application") version "8.7.3"
    id("org.jetbrains.kotlin.android") version "1.9.25"
}
android {
    namespace = "kr.pleosguide"
    compileSdk = 35
    buildToolsVersion = "35.0.0"
    useLibrary("android.car", false)
    defaultConfig {
        applicationId = "kr.pleosguide"
        minSdk = 28
        targetSdk = 32
        versionCode = 1
        versionName = "1.0.0"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { buildConfig = true }
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
            val key = System.getenv("PLEOS_KEYSTORE")
            if (!key.isNullOrBlank()) {
                signingConfig = signingConfigs.create("submission") {
                    storeFile = file(key)
                    storePassword = System.getenv("PLEOS_STORE_PASSWORD")
                    keyAlias = "submission"
                    keyPassword = System.getenv("PLEOS_KEY_PASSWORD")
                }
            }
        }
    }
}
dependencies {
    implementation("ai.pleos.playground:Vehicle:2.3.2")
    implementation("ai.pleos.playground:SpeechToText:3.3.1")
    implementation("ai.pleos.playground:TextToSpeech:3.3.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.3")
    testImplementation("junit:junit:4.13.2")
}
