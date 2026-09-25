## LLM Wiki sync

Po každé změně, která mění uživatelské chování, provoz, integraci, autentizaci,
datový kontrakt nebo nasazení, aktualizuj odpovídající entitu a měsíční
changelog v repozitáři `ITKytaryDevTeam/Kytary.Wiki`. Wiki je zdroj aktuálního
stavu; neopisuj do ní tajné hodnoty ani osobní údaje mimo nezbytné firemní
e-maily. Nainstalované hooky z `Kytary.Wiki/tools/wiki-sync` jsou blokující
bezpečnostní síť a nesmějí se obcházet. Přístupové politiky spravuje centrálně
repozitář `coolify-kytary`, nikoli tento repozitář.

Tato služba je headless MCP server. Nepřidávej do ní uživatelské menu jen kvůli
zobrazení allowlistu; její aktuální přístupová politika se eviduje centrálně.
