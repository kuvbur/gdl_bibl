cd /d %~dp0
cd ..
cd ..

set "gdl_from1_dir=%cd%\_ArchiBibl 22"
set "gdl_from2_dir=%cd%\_Standart"
set "gdl_from3_dir=%cd%\_MEP"

set "gdl_1_dir=%cd%\gdl_bibl\gsm\_ArchiBibl 22"
set "gdl_2_dir=%cd%\gdl_bibl\gsm\_Standart"
set "gdl_3_dir=%cd%\gdl_bibl\gsm\_MEP"

set "hsf_1_dir=%cd%\gdl_bibl\hsf\_ArchiBibl 22"
set "hsf_2_dir=%cd%\gdl_bibl\hsf\_Standart"
set "hsf_3_dir=%cd%\gdl_bibl\hsf\_MEP"

set "bat_dir=%cd%\gdl_bibl\bat"

rm -rf "%gdl_1_dir%"
rm -rf "%hsf_1_dir%"
MD "%gdl_1_dir%"
MD "%hsf_1_dir%"
ROBOCOPY "%gdl_from1_dir%" "%gdl_1_dir%" /E
cd gdl_bibl
cd lcf
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  createcontainer  archbib25.lcf -compress 9 "%gdl_1_dir%">"%bat_dir%\_lcf_log.txt"

cd ..
cd hsf
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  l2hsf "%gdl_1_dir%" "%hsf_1_dir%" >"%bat_dir%\_hsf_log.txt"


rm -rf "%gdl_2_dir%"
rm -rf "%hsf_2_dir%"
MD "%gdl_2_dir%"
MD "%hsf_2_dir%"
cd ..
cd ..
ROBOCOPY "%gdl_from2_dir%" "%gdl_2_dir%" /E
cd gdl_bibl
cd lcf
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  createcontainer  standart25.lcf -compress 9 "%gdl_2_dir%">"%bat_dir%\_lcf_log.txt"
cd ..
cd hsf
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  l2hsf "%gdl_2_dir%" "%hsf_2_dir%" >"%bat_dir%\_hsf_log.txt"

rm -rf "%gdl_3_dir%"
rm -rf "%hsf_3_dir%"
MD "%gdl_3_dir%"
MD "%hsf_3_dir%"
cd ..
cd ..
ROBOCOPY "%gdl_from3_dir%" "%gdl_3_dir%" /E
cd gdl_bibl
cd lcf
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  createcontainer  mep25.lcf -compress 9 "%gdl_3_dir%">"%bat_dir%\_lcf_log.txt"
cd ..
cd hsf
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  l2hsf "%gdl_3_dir%" "%hsf_3_dir%" >"%bat_dir%\_hsf_log.txt"