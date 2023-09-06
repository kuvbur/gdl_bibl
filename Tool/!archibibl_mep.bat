cd /d %~dp0
cd ..
set "converter=C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"
set "tool_dir=%cd%\Tool"
set "gdl_dir=%cd%\gdl"
set "hsf_dir=%cd%\hsf"
set "lcf_dir=%cd%\lcf"

set "gdl_1_dir=%gdl_dir%\_ArchiBibl 22"
set "gdl_3_dir=%gdl_dir%\_MEP"

set "hsf_1_dir=%hsf_dir%\_ArchiBibl 22"
set "hsf_3_dir=%hsf_dir%\_MEP"

set "lcf_1=%lcf_dir%\archbib24.lcf"
set "lcf_3=%lcf_dir%\mep24.lcf"

RD /S /Q  "%hsf_1_dir%"
RD /S /Q  "%hsf_3_dir%"
MD "%hsf_1_dir%"
MD "%hsf_3_dir%"
cd "%hsf_dir%"
"%converter%"   l2hsf "%gdl_1_dir%" "%hsf_1_dir%" >"%tool_dir%\_ArchiBibl 22_hsf_log.txt"
"%converter%"   l2hsf "%gdl_3_dir%" "%hsf_3_dir%" >"%tool_dir%\_MEP_hsf_log.txt"

cd "%lcf_dir%"
"%converter%" createcontainer "%lcf_1%" -compress 9 "%gdl_1_dir%">"%tool_dir%\_ArchiBibl 22_log.txt"
"%converter%" createcontainer "%lcf_3%" -compress 9 "%gdl_3_dir%">"%tool_dir%\_MEP_log.txt"

TIMEOUT /T 1

cd ..
cd ..

ROBOCOPY "%cd%\gdl_macro\lcf" "%lcf_dir%" /E>"%tool_dir%\_copy_log.txt"
ROBOCOPY "%cd%\gdl_macro\lcf" "%cd%\LCF24" /E>"%tool_dir%\_copy_log.txt"

ROBOCOPY "%lcf_dir%" "%cd%\LCF24" archbib24.lcf /E>"%tool_dir%\_copy_log.txt"
ROBOCOPY "%lcf_dir%" "%cd%\LCF24" mep24.lcf /E>"%tool_dir%\_copy_log.txt"