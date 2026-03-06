
# Building APK works !!!

You should have docker, adb, and a device/phone in dev mode ! (Currently it works, at least for me (Ubuntu 24.04.4 LTS & Pixel8))

**TODO:** The process need to be improved, to make the process easier !

In CLI, inside this folder, follow these steps :

## Ensure htag app is working
Ensure the htag app is working (using the runner `WebApp(DemoApp).run()`):

    uv run main.py

notes:

- Currently only with the runner *WebApp* !
- It should start on port localhost:13333 (`WebApp(DemoApp).run( host="127.0.0.1", port=13333 )`)

## Build the APK
To build the APK, run :

    uv run htagm apk main.py 

notes:

- It will create a default `buildozer.spec` file (if not already existing), you can change it later.
- First run it can takes 5 to 10 minutes, subsequent runs are faster.
- The apk should be generated in the `bin` folder (as `main-1.0-arm64-v8a-debug.apk`).
- As you don't set '--tv' option, it will be built for phone (arm64-v8a).

## Install the APK

Device (an arm64-v8a) must be connected with usb/adb, you should see :

    adb devices

    List of devices attached
    4B291EDJG103XD	device

And install the APK, on the device, with:

    adb install -r -t bin/main-1.0-arm64-v8a-debug.apk

### Installation Failure (Signature Mismatch)
If you get `INSTALL_FAILED_UPDATE_INCOMPATIBLE`, it means the existing app has a different signature. Uninstall it first:

    adb uninstall org.htag.main

## To debug

    adb logcat | grep --line-buffered "org.htag.main"

or (need to install pidcat) 

    pidcat org.htag.main
