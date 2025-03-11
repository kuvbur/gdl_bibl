cd /d %~dp0
cd ..
set "converter=C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"
set "tool_dir=%cd%\Tool"
set "gdl_dir=%cd%\gdl"
set "hsf_dir=%cd%\hsf"
set "lcf_dir=%cd%\lcf"

set "gdl_3_dir=%gdl_dir%\_MEP"

set "hsf_3_dir=%hsf_dir%\_MEP"

set "lcf_3=%lcf_dir%\mep24.lcf"

RD /S /Q  "%hsf_3_dir%"

MD "%hsf_3_dir%"

cd "%hsf_dir%"

"%converter%"   l2hsf -l CYR "%gdl_3_dir%" "%hsf_3_dir%" >"%tool_dir%\log\_MEP_hsf_log.txt"

cd "%lcf_dir%"

"%converter%" createcontainer "%lcf_3%" -compress 9 "%gdl_3_dir%">"%tool_dir%\log\_MEP_log.txt"

python "%tool_dir%\hsf2text.py">"%tool_dir%\log\_copy_log.txt"

TIMEOUT /T 1

cd ..
cd ..

ROBOCOPY "%cd%\gdl_macro\lcf" "%lcf_dir%" /E>"%tool_dir%\log\_copy_log.txt"
ROBOCOPY "%cd%\gdl_macro\lcf" "%cd%\LCF25" /E>"%tool_dir%\log\_copy_log.txt"

ROBOCOPY "%lcf_dir%" "%cd%\LCF25" mep24.lcf /E>"%tool_dir%\log\_copy_log.txt"