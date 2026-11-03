import pathlib, zipfile, sys, shutil
app=sys.argv[1]
root=pathlib.Path("buildsrc")/app
assets=root/"app/src/main/assets"
assets.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(app+".zip") as z:
    for info in z.infolist():
        p=pathlib.PurePosixPath(info.filename)
        if not p.parts or p.parts[0]!=app: continue
        rel=pathlib.Path(*p.parts[1:])
        if not rel.parts or info.is_dir(): continue
        target=assets/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(z.read(info))
(root/"settings.gradle").write_text("pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\ndependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }\nrootProject.name = '"+app+"'\ninclude ':app'\n")
(root/"gradle.properties").write_text("android.useAndroidX=true\nandroid.enableJetifier=true\n")
(root/"build.gradle").write_text("plugins { id 'com.android.application' version '8.7.3' apply false }\n")
(root/"app/build.gradle").write_text("""plugins { id 'com.android.application' }
android {
 namespace 'com.nestor.offlineapp'
 compileSdk 35
 defaultConfig {
  applicationId 'com.nestor."""+app.lower()+"""'
  minSdk 24
  targetSdk 28
  versionCode 1
  versionName '1.0'
 }
}
dependencies { implementation 'androidx.webkit:webkit:1.12.1' }
""")
import cairosvg
icon_dir=root/"app/src/main/res/drawable-nodpi"
icon_dir.mkdir(parents=True,exist_ok=True)
cairosvg.svg2png(url=str(pathlib.Path("icons")/(app+".svg")),write_to=str(icon_dir/"app_icon.png"),output_width=512,output_height=512)
manifest=root/"app/src/main/AndroidManifest.xml"
manifest.parent.mkdir(parents=True,exist_ok=True)
manifest.write_text("""<manifest xmlns:android="http://schemas.android.com/apk/res/android">
<application android:label='"""+app+"""' android:theme="@android:style/Theme.Material.Light.NoActionBar" android:usesCleartextTraffic="true" android:icon="@drawable/app_icon" android:roundIcon="@drawable/app_icon">
<activity android:name=".MainActivity" android:exported="true" android:configChanges="orientation|screenSize|keyboardHidden">
<intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>
</activity></application></manifest>""")
java=root/"app/src/main/java/com/nestor/offlineapp/MainActivity.java"
java.parent.mkdir(parents=True,exist_ok=True)
java.write_text("""package com.nestor.offlineapp;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import androidx.webkit.WebViewAssetLoader;
import androidx.webkit.WebViewAssetLoader.AssetsPathHandler;
import androidx.webkit.WebViewClientCompat;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
public class MainActivity extends Activity {
 WebView web;
 @Override public void onCreate(Bundle b) {
  super.onCreate(b);
  web=new WebView(this);setContentView(web);
  WebSettings s=web.getSettings();
  s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);
  s.setAllowFileAccess(false);s.setAllowContentAccess(false);
  s.setMediaPlaybackRequiresUserGesture(false);
  final WebViewAssetLoader loader=new WebViewAssetLoader.Builder().addPathHandler("/assets/",new AssetsPathHandler(this)).build();
  web.setWebViewClient(new WebViewClientCompat(){
   @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest req){return loader.shouldInterceptRequest(req.getUrl());}
  });
  web.setWebChromeClient(new WebChromeClient());
  web.loadUrl("https://appassets.androidplatform.net/assets/index.html");
 }
 @Override public void onBackPressed(){if(web.canGoBack())web.goBack();else super.onBackPressed();}
}
""")
print("Prepared",app,"with",len(list(assets.rglob("*"))),"assets")
