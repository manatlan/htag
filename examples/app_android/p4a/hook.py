import os
import shutil
from pathlib import Path
from pythonforandroid.toolchain import ToolchainCL

def after_apk_build(toolchain: ToolchainCL):
    ############################################################################
    ## Change assets/_load.html
    ############################################################################
    asset_html_file = Path(toolchain._dist.dist_dir) /"src"/ "main" / "assets" / "_load.html"
    asset_html_file.write_text("<html><head><style>body {background:black;color:white;}</style></head><body>pre-loading...</body></html>", encoding="utf-8")

    ############################################################################
    ## Change AndroidManifest.xml
    ############################################################################
    manifest_file = Path(toolchain._dist.dist_dir) / "src" / "main" / "AndroidManifest.xml"
    
    #-----------------------------------------------------------------------
    content = manifest_file.read_text(encoding="utf-8")

    # content=content.replace(
    #     """<category android:name="android.intent.category.LAUNCHER" />""",
    #     """<category android:name="android.intent.category.LAUNCHER" /><category android:name="android.intent.category.LEANBACK_LAUNCHER" />""",
    # )
        
    # content = content.replace(
    #     '<activity ',
    #     '<activity android:banner="@drawable/presplash" android:icon="@mipmap/icon" android:logo="@mipmap/icon" ',
    # )
    
    # assert 'android:banner="@drawable/presplash"' in content
    # assert 'android.intent.category.LEANBACK_LAUNCHER' in content
    
    #-----------------------------------------------------------------------
    manifest_file.write_text(content, encoding="utf-8")
    
    print("============================================== MANIFEST")
    print(content)
    print("==============================================")