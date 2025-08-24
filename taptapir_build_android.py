import os
import subprocess
import shutil

def generate_webview_android_app(app_name,
                                  package_name,
                                  version:int,
                                  project_dir=None,
                                  html_content=None,
                                  icon_path=None,
                                  include_admob=True,
                                  has_reward_ads=False,
                                  admob_app_id='ca-app-pub-3940256099942544~3347511713',
                                  banner_bottom_ad_unit_id=None,
                                  release=False,
                                  ):
    """
    Generates an Android WebView app project with optional AdMob support.

    Args:
        app_name (str): The app's display name.
        package_name (str): The app's package name.
        html_content (str): The HTML content for index.html. If None, uses a default template.
        include_admob (bool): Whether to include AdMob banner support.
        project_dir (str): Directory to generate the project in.
    """
    project_dir = project_dir if project_dir is not None else app_name

    os.makedirs(project_dir, exist_ok=True)
    os.chdir(project_dir)

    paths = [
        "app/src/main/kotlin/" + package_name.replace(".", "/"),
        "app/src/main/res/layout",
        "app/src/main/assets",
        "app/src/main/res/values",
        "app/src/main/res/mipmap-anydpi"
    ]
    for path in paths:
        os.makedirs(path, exist_ok=True)

    # build.gradle (root)
    with open("build.gradle", "w") as f:
        f.write("""\
// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id 'com.android.application' version '8.4.2' apply false
    id 'com.android.library' version '8.4.2' apply false
    id 'org.jetbrains.kotlin.android' version '2.2.0' apply false
}
""")
    with open('settings.gradle', 'w') as f:
        f.write(f"""\
pluginManagement {{
    repositories {{
        gradlePluginPortal()
        google()
        mavenCentral()
    }}
}}
rootProject.name = "{app_name}"
include ':app'
""")


    with open('gradle.properties', 'w') as f:
        f.write("""\
android.useAndroidX=true
android.enableJetifier=true
""")

    # app/build.gradle
    with open("app/build.gradle", "w") as f:
        f.write(f"""\
plugins {{
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}}

android {{
    namespace '{package_name}'
    compileSdk 33

    defaultConfig {{
        applicationId "{package_name}"
        minSdk 24
        targetSdk 33
        versionCode {version}
        versionName "{version}"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }}

    buildTypes {{
        release {{
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            signingConfig signingConfigs.debug
        }}
        debug {{
            minifyEnabled false     // Disable R8/ProGuard for debug builds
            shrinkResources false   // Optional: also disable resource shrinking
            debuggable true
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
    kotlinOptions {{
        jvmTarget = '1.8'
    }}
    buildFeatures {{
        viewBinding true
    }}

}}

repositories {{
    google()
    mavenCentral()
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.8.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.5.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.3'
    implementation 'androidx.navigation:navigation-fragment-ktx:2.5.2'
    implementation 'androidx.navigation:navigation-ui-ktx:2.5.2'
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'

    implementation 'com.google.android.gms:play-services-ads:22.2.0'
}}
""")

    # AndroidManifest.xml
    with open("app/src/main/AndroidManifest.xml", "w") as f:
        f.write(f"""\
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <application
        android:allowBackup="true"
        android:label="{app_name}"
        android:icon="@mipmap/icon"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar"
        android:supportsRtl="true"
        tools:targetApi="34">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Sample AdMob app ID: ca-app-pub-3940256099942544~3347511713 -->
        <meta-data
            android:name="com.google.android.gms.ads.APPLICATION_ID"
            android:value="{admob_app_id}"/>
    </application>

    <uses-permission android:name="com.google.android.gms.permission.AD_ID"/>

</manifest>
<!-- under application:
android:icon="@mipmap/ic_launcher"
android:roundIcon="@mipmap/ic_launcher_round"
-->
<!-- android:supportsRtl="true" -->
<!-- android:theme="@style/Theme.CMYKSwap" -->

<!-- android:exported="true" -->
            <!-- android:theme="@style/Theme.CMYKSwap"> -->
""")

    # activity_main.xml
    banner_ad_code = f"""\
<com.google.android.gms.ads.AdView
    android:id="@+id/adView"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_alignParentBottom="true"
    android:layout_centerHorizontal="true"
    android:layout_gravity="bottom"
    app:adSize="BANNER"
    app:adUnitId="{banner_bottom_ad_unit_id}"
    />
""" if include_admob and banner_bottom_ad_unit_id else ''

    with open("app/src/main/res/layout/activity_main.xml", "w") as f:
        f.write(f"""\
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fitsSystemWindows="true"
    android:background="#000000"
    tools:context=".MainActivity">


    <WebView
        android:id="@+id/MyWebView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:layout_marginBottom="50dp"
        tools:layout_editor_absoluteX="0dp"
        tools:layout_editor_absoluteY="424dp"/>

    {banner_ad_code}
</RelativeLayout>
""")

    # MainActivity.kt
    kotlin_path = f"app/src/main/kotlin/{package_name.replace('.', '/')}/MainActivity.kt"
    ad_imports = ''
    if admob_app_id:
        ad_imports = '''\
import com.google.android.gms.ads.AdRequest
import com.google.android.gms.ads.AdView
import com.google.android.gms.ads.MobileAds
import com.google.android.gms.ads.rewarded.RewardedAd
import com.google.android.gms.ads.rewarded.RewardItem
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback
'''
    ad_loading_code = '''\
// load banner ad when page has finished loading
        ad_view = findViewById(R.id.adView)

        web_view.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                val ad_request = AdRequest.Builder().build()
                ad_view.loadAd(ad_request)
            }
        }
        ''' if include_admob and admob_app_id else ''

    reward_ad_logic = '''\
// load_reward_ad()
fun load_reward_ad() {
        val ad_request = AdRequest.Builder().build()
        RewardedAd.load(this, "YOUR_AD_UNIT_ID", ad_request, object : RewardedAdLoadCallback() {
            override fun onAdLoaded(ad: RewardedAd) {
                rewarded_ad = ad
            }
        })
    }


''' if include_admob and admob_app_id else ''

    show_reward_ad_function = '''\
rewarded_ad?.show(this) { _: RewardItem ->
        val js = "javascript:onRewardEarned()"
        web_view.evaluateJavascript(js, null)
    } ?: load_reward_ad()
    ''' if include_admob and admob_app_id and has_reward_ads else 'println("Reward ads not supported.")'

    with open(kotlin_path, "w") as f:
        f.write(f"""\
package {package_name}

import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.WebChromeClient
import androidx.appcompat.app.AppCompatActivity
import android.webkit.WebSettings

import android.os.Build
import android.util.Log
import android.widget.Toast
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest

{ad_imports}

class MainActivity : AppCompatActivity() {{
    private lateinit var web_view: WebView
    {'private lateinit var ad_view: AdView' if admob_app_id else ''}
    {'private var rewarded_ad: RewardedAd? = null' if admob_app_id else ''}

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        web_view = findViewById(R.id.MyWebView)
        web_view.settings.javaScriptEnabled = true
        web_view.settings.domStorageEnabled = true
        web_view.settings.allowFileAccess = true
        web_view.settings.allowFileAccessFromFileURLs = true
        web_view.settings.allowUniversalAccessFromFileURLs = true
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
            web_view.settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }}

        // Enable WebView debugging for Chrome DevTools
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {{
            WebView.setWebContentsDebuggingEnabled(true)
        }}
        // Handle page load errors
        web_view.webViewClient = object : WebViewClient() {{
            override fun onReceivedError(
                view: WebView,
                request: WebResourceRequest,
                error: WebResourceError
            ) {{
                Log.e("WebViewError", "Error loading ${{request.url}}: ${{error.description}}")
            }}
        }}

        {ad_loading_code}

        web_view.webChromeClient = WebChromeClient()
        web_view.loadUrl("file:///android_asset/index.html")
        web_view.addJavascriptInterface(WebAppInterface(), "Android")

        {'MobileAds.initialize(this)' if admob_app_id else ''}
    }}

    {reward_ad_logic}

    fun show_reward_ad() {{
        {show_reward_ad_function}
    }}

    inner class WebAppInterface {{
        @android.webkit.JavascriptInterface
        fun show_reward_ad() {{
            runOnUiThread {{
                this@MainActivity.show_reward_ad()
            }}
        }}
        @android.webkit.JavascriptInterface
        fun reportJsError(message: String, source: String, line: Int, col: Int, error: String?) {{
            val errorMsg = "JS Error: $message at $source:$line:$col Stack: $error"
            Log.e("WebViewJS", errorMsg)
            // Optional: show error on screen for debugging
            runOnUiThread {{
                Toast.makeText(this@MainActivity, errorMsg, Toast.LENGTH_LONG).show()
            }}
        }}
    }}
}}
""")

    # index.html
    if html_content is None:
        html_content = """\
<!DOCTYPE html>
<html>
<head>
    <title>My WebView App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>Hello from WebView!</h1>
    <p>This is a local HTML page displayed inside your Android app.</p>
</body>
</html>
"""
    with open("app/src/main/assets/index.html", "w") as f:
        f.write(html_content)

    if not icon_path.exists():
        raise Exception('icon not found:', icon_path)

    shutil.copy(icon_path.resolve(), 'app/src/main/res/mipmap-anydpi/icon.png')

    print(f"✅ Project '{app_name}' generated successfully in '{project_dir}'")
    print("Next steps:")
    print("1) Start an emulator: `emulator -avd MyEmulator` (see available devices with `emulator -list-avds`)")
    print("2) Install using 'adb install -r app/build/outputs/apk/debug/app-debug.apk' (different terminal from the one the emulator is running in).")
    print(f"3) Start app with: `adb shell am start -n {package_name}/.MainActivity`")

    # Return to original working directory if you need in batch scripts
    if not os.path.exists("./gradlew"):
        subprocess.run(["gradle", "wrapper"])
    os.chmod("./gradlew", 0o755)
    subprocess.run(['./gradlew', ':app:assembleDebug' if not release else 'bundleRelease'])
    os.chdir("..")
    os.chdir("..")
