adb --version
adb push scrcpy-server.jar /data/local/tmp/scrcpy-server.jar
adb shell "chmod 755 /data/local/tmp/scrcpy-server.jar"
adb shell "CLASSPATH=/data/local/tmp/scrcpy-server.jar app_process / com.genymobile.scrcpy.Server 3.3.4 tunnel_forward=true control=true audio=false max_size=1024 bit_rate=2000000 shell=true"