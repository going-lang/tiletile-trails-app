#!/usr/bin/env python3
"""Configure Appodeal in the generated Capacitor Android project.

Run from the repository root after `npx cap add android`.
Requires the APPODEAL_APP_KEY environment variable.
"""
import os
import re
import sys
from pathlib import Path

REPO_MARKER = "artifactory.appodeal.com/appodeal"
APPODEAL_REPO = 'maven { url = uri("https://artifactory.appodeal.com/appodeal") }'

DEPENDENCIES = [
    'implementation("com.appodeal.ads.sdk:core:4.4.0")',
    'implementation("com.appodeal.ads.sdk.adapters:amazon:12.0.0.0")',
    'implementation("com.appodeal.ads.sdk.adapters:applovin:13.6.3.0")',
    'implementation("com.appodeal.ads.sdk.adapters:applovin_max:13.6.3.1")',
    'implementation("com.appodeal.ads.sdk.adapters:bidmachine:3.7.1.0")',
    'implementation("com.appodeal.ads.sdk.adapters:bidon:0.14.0.0")',
    'implementation("com.appodeal.ads.sdk.adapters:bigo_ads:5.9.0.0")',
    'implementation("com.appodeal.ads.sdk.adapters:chartboost:9.10.2.0")',
    'implementation("com.appodeal.ads.sdk.adapters:dt_exchange:8.4.6.0")',
    'implementation("com.appodeal.ads.sdk.adapters:iab:1.8.1.1")',
    'implementation("com.appodeal.ads.sdk.adapters:inmobi:11.3.0.0")',
    'implementation("com.appodeal.ads.sdk.adapters:ironsource:9.4.4.0")',
    'implementation("com.appodeal.ads.sdk.adapters:level_play:9.4.4.0")',
    'implementation("com.appodeal.ads.sdk.adapters:mintegral:17.1.61.0")',
    'implementation("com.appodeal.ads.sdk.adapters:mobilefuse:1.11.0.0")',
    'implementation("com.appodeal.ads.sdk.adapters:moloco:4.3.1.0")',
    'implementation("com.appodeal.ads.sdk.adapters:my_target:5.47.1.0")',
    'implementation("com.appodeal.ads.sdk.adapters:ogury:6.2.0.0")',
    'implementation("com.appodeal.ads.sdk.adapters:pubmatic:4.10.0.0")',
    'implementation("com.appodeal.ads.sdk.adapters:smaato:22.7.2.0")',
    'implementation("com.appodeal.ads.sdk.adapters:startio:5.2.4.0")',
    'implementation("com.appodeal.ads.sdk.adapters:taurusx:1.12.2.0")',
    'implementation("com.appodeal.ads.sdk.adapters:unity_ads:4.17.0.0")',
    'implementation("com.appodeal.ads.sdk.adapters:verve:3.7.1.0")',
    'implementation("com.appodeal.ads.sdk.adapters:vungle:7.7.4.0")',
    'implementation("com.appodeal.ads.sdk.adapters:yandex:7.17.0.0")',
]

NETWORK_SECURITY_XML = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
"""

MAIN_ACTIVITY_JAVA = """package com.tiletrails.game;

import android.os.Bundle;

import androidx.annotation.Nullable;

import com.appodeal.ads.Appodeal;
import com.appodeal.ads.initializing.ApdInitializationCallback;
import com.appodeal.ads.initializing.ApdInitializationError;
import com.getcapacitor.BridgeActivity;

import java.util.List;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        int adTypes = Appodeal.BANNER | Appodeal.INTERSTITIAL;

        Appodeal.initialize(
                this,
                "__APPODEAL_KEY__",
                adTypes,
                new ApdInitializationCallback() {
                    @Override
                    public void onInitializationFinished(
                            @Nullable List<ApdInitializationError> errors) {
                        Appodeal.show(MainActivity.this, Appodeal.BANNER_BOTTOM);
                    }
                }
        );
    }
}
"""


def fail(message):
    sys.exit("ERROR: " + message)


def first_existing(*paths):
    for p in paths:
        path = Path(p)
        if path.exists():
            return path
    return None


def configure_settings():
    settings = first_existing("android/settings.gradle", "android/settings.gradle.kts")
    if settings is None:
        fail("android/settings.gradle was not generated")

    text = settings.read_text()

    if REPO_MARKER not in text:
        drm = re.search(r"dependencyResolutionManagement\s*\{", text)
        if drm:
            repos = re.search(r"\brepositories\s*\{", text[drm.start():])
            if not repos:
                fail("no repositories block inside dependencyResolutionManagement")
            pos = drm.start() + repos.end()
            text = text[:pos] + "\n        " + APPODEAL_REPO + text[pos:]
        else:
            text += (
                "\n"
                "dependencyResolutionManagement {\n"
                "    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)\n"
                "    repositories {\n"
                "        google()\n"
                "        mavenCentral()\n"
                "        " + APPODEAL_REPO + "\n"
                "    }\n"
                "}\n"
            )
        settings.write_text(text)

    print("Appodeal Maven repository configured in", settings)


def configure_app_gradle():
    app_gradle = first_existing("android/app/build.gradle", "android/app/build.gradle.kts")
    if app_gradle is None:
        fail("android/app/build.gradle was not generated")

    text = app_gradle.read_text()

    if "com.appodeal.ads.sdk:core" not in text:
        # Top-level `dependencies {` only, not one nested in another block.
        match = re.search(r"^dependencies\s*\{", text, flags=re.MULTILINE)
        if not match:
            fail("top-level dependencies block not found in " + str(app_gradle))
        block = "".join("    " + dep + "\n" for dep in DEPENDENCIES)
        text = text[:match.end()] + "\n" + block + text[match.end():]
        app_gradle.write_text(text)

    print("Appodeal dependencies configured in", app_gradle)


def configure_network_security():
    xml_dir = Path("android/app/src/main/res/xml")
    xml_dir.mkdir(parents=True, exist_ok=True)
    (xml_dir / "network_security_config.xml").write_text(NETWORK_SECURITY_XML)

    manifest = Path("android/app/src/main/AndroidManifest.xml")
    if not manifest.exists():
        fail("AndroidManifest.xml not found")

    text = manifest.read_text()
    if "android:networkSecurityConfig=" not in text:
        text = text.replace(
            "<application",
            '<application android:networkSecurityConfig="@xml/network_security_config"',
            1,
        )
        manifest.write_text(text)

    print("Network security config applied.")


def write_main_activity():
    key = os.environ.get("APPODEAL_APP_KEY", "")
    if not key:
        fail("APPODEAL_APP_KEY is not set")

    activity = Path("android/app/src/main/java/com/tiletrails/game/MainActivity.java")
    activity.parent.mkdir(parents=True, exist_ok=True)
    activity.write_text(MAIN_ACTIVITY_JAVA.replace("__APPODEAL_KEY__", key))

    print("MainActivity.java written.")


def main():
    configure_settings()
    configure_app_gradle()
    configure_network_security()
    write_main_activity()
    print("Appodeal configuration completed.")


if __name__ == "__main__":
    main()
