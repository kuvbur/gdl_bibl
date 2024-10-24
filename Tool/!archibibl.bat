cd /d %~dp0
cd ..
set "converter=C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"
set "tool_dir=%cd%\Tool"
set "gdl_dir=%cd%\gdl"
set "hsf_dir=%cd%\hsf"
set "lcf_dir=%cd%\lcf"

set "gdl_1_dir=%gdl_dir%\_ArchiBibl"

set "hsf_1_dir=%hsf_dir%\_ArchiBibl"
set "lcf_1=%lcf_dir%\archbib24.lcf"


RD /S /Q  "%hsf_1_dir%"

MD "%hsf_1_dir%"

cd "%hsf_dir%"
"%converter%"   l2hsf -l CYR "%gdl_1_dir%" "%hsf_1_dir%" >"%tool_dir%\log\_ArchiBibl_hsf_log.txt"

cd "%lcf_dir%"
"%converter%" createcontainer "%lcf_1%" -compress 9 "%gdl_1_dir%">"%tool_dir%\log\_ArchiBibl_log.txt"
TIMEOUT /T 1
python "%tool_dir%\build_lcf.py">"%tool_dir%\log\_copy_log.txt">"%tool_dir%\log\_ArchiBibl_log.txt"
TIMEOUT /T 1
python "%tool_dir%\hsf2text.py">"%tool_dir%\log\_copy_log.txt">"%tool_dir%\log\_ArchiBibl_log.txt"

cd ..
cd ..

ROBOCOPY "%cd%\gdl_macro\lcf" "%lcf_dir%" /E>"%tool_dir%\log\_copy_log.txt"
ROBOCOPY "%cd%\gdl_macro\lcf" "%cd%\LCF24" /E>"%tool_dir%\log\_copy_log.txt"
ROBOCOPY "%lcf_dir%" "%cd%\LCF24" archbib24.lcf /E>"%tool_dir%\log\_copy_log.txt"
