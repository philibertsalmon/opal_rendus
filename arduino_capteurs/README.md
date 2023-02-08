Le but de ce code est de d'envoyer les valeurs de température, humidité et de concentration en CO2 quand il recoit un signal Bluetooth de "0" et de renvoyer c'est donné à celui qui a fait la requete sous le format suivant "température(°c),humidité(%),CO2(ppm)"

Nous utilisons un capteur DHT11 et CO2_Sensor_SKU_SEN0159

Pour pouvoir exécuter le code veuillez installer la librairie "DHT sensor library by Adafruit / Arduino library for DHT11, DHT22 etc Temp & Humidity Sensors"

Pour la librairie PololuLedStrip.h
1. Dans l'IDE Arduino, ouvrez le menu "Sketch", sélectionnez "Include Library", puis
   "Manage Libraries...".
2. Recherchez "PololuLedStrip".
3. Cliquez sur l'entrée PololuLedStrip dans la liste.
4. Cliquez sur "Installer".

Téléversez le code sur l'Arduino pour lui faire exécuter 

Information : la lumière du capteur Bluetooth clignote en continu quand il n'est pas connecté et clignote par intermitance quand il est connecté 