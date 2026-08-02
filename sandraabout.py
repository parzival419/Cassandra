[1mdiff --git a/cassandra/__main__.py b/cassandra/__main__.py[m
[1mindex aa5e49a..d56647a 100644[m
[1m--- a/cassandra/__main__.py[m
[1m+++ b/cassandra/__main__.py[m
[36m@@ -4,6 +4,7 @@[m [mfrom __future__ import annotations[m
 [m
 from pprint import pprint[m
 [m
[32m+[m[32mfrom cassandra.about import APP_NAME, VERSION, DESCRIPTION[m
 from cassandra.observation import EnvironmentInfo, ObservationEngine[m
 from cassandra.observation.sensors import ([m
     ClipboardSensor,[m
[36m@@ -13,7 +14,7 @@[m [mfrom cassandra.observation.sensors import ([m
 [m
 [m
 def build_sensor_registry() -> SensorRegistry:[m
[31m-    """Build the sensor profile used by the local demonstration."""[m
[32m+[m[32m    """Build the default sensor profile."""[m
 [m
     registry = SensorRegistry()[m
 [m
[36m@@ -24,9 +25,11 @@[m [mdef build_sensor_registry() -> SensorRegistry:[m
 [m
 [m
 def main() -> None:[m
[31m-    """Start Cassandra and capture a test observation."""[m
[32m+[m[32m    """Start Cassandra."""[m
 [m
[31m-    print("Starting Cassandra...\n")[m
[32m+[m[32m    print(f"{APP_NAME} v{VERSION}")[m
[32m+[m[32m    print(DESCRIPTION)[m
[32m+[m[32m    print()[m
 [m
     environment = EnvironmentInfo([m
         name="Development Sandbox",[m
[36m@@ -35,6 +38,16 @@[m [mdef main() -> None:[m
 [m
     registry = build_sensor_registry()[m
 [m
[32m+[m[32m    print(f"Environment : {environment.name}")[m
[32m+[m[32m    print(f"Sensors     : {len(registry)}")[m
[32m+[m[32m    print()[m
[32m+[m
[32m+[m[32m    for sensor in registry:[m
[32m+[m[32m        print(f"✓ {sensor.name}")[m
[32m+[m
[32m+[m[32m    print()[m
[32m+[m[32m    print("Collecting observation...\n")[m
[32m+[m
     engine = ObservationEngine([m
         environment=environment,[m
         sensors=registry,[m
