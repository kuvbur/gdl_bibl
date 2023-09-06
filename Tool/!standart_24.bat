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

"%converter%" createcontainer "%lcf_2%" -compress 9 "%gdl_2_dir%">"%tool_dir%\_Standart_lcf_log.txt"

TIMEOUT /T 5

cd ..
cd ..

ROBOCOPY "%cd%\gdl_macro\lcf" "%cd%\LCF24" /E>"%tool_dir%\_copy_log.txt"
ROBOCOPY "%cd%\gdl_macro\lcf" "%cd%\LCF24" /E>"%tool_dir%\_copy_log.txt"
ROBOCOPY "%lcf_dir%" "%cd%\LCF24" standart24.lcf /E>"%tool_dir%\_copy_log.txt"
