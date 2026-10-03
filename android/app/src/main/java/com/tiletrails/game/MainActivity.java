package com.tiletrails.game;

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
                "APPODEAL_APP_KEY",
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
