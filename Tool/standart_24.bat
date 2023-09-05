cd /d %~dp0
cd ..
set "converter=C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"
set "tool_dir=%cd%\Tool"
set "gdl_dir=%cd%\gdl"
set "hsf_dir=%cd%\hsf"
set "lcf_dir=%cd%\lcf"

set "gdl_2_dir=%gdl_dir%\_Standart"
set "hsf_2_dir=%hsf_dir%\_Standart"
set "lcf_2=%lcf_dir%\standart24.lcf"

RD /S /Q  "%hsf_2_dir%"
MD "%hsf_2_dir%"
cd "%hsf_dir%"
"%converter%"   l2hsf -compatibility 25 "%gdl_2_dir%" "%hsf_2_dir%" >"%tool_dir%\_Standart_hsf_log.txt"

RD /S /Q "%lcf_2%"
"%converter%" createcontainer %lcf_2% -compress 9 "%gdl_2_dir%">"%tool_dir%\_Standart_lcf_log.txt"

TIMEOUT /T 10

ROBOCOPY "%lcf%" "C:\Users\kuvbur\YandexDisk\sourse\LCF24" /E
ROBOCOPY "C:\Users\kuvbur\YandexDisk\sourse\gdl_macro\lcf" "%lcf_dir%" /E
ROBOCOPY "C:\Users\kuvbur\YandexDisk\sourse\gdl_macro\lcf" "C:\Users\kuvbur\YandexDisk\sourse\LCF24" /E
