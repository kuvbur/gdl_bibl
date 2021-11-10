cd /d %~dp0
cd ..
cd ..
set "gdl_1_dir=%cd%\_ArchiBibl 22"
set "gdl_2_dir=%cd%\_Standart"
set "gdl_3_dir=%cd%\_MEP"

set "xml_1_dir=%cd%\gdl_bibl\xml\_ArchiBibl 22"
set "xml_2_dir=%cd%\gdl_bibl\xml\_Standart"
set "xml_3_dir=%cd%\gdl_bibl\xml\_MEP"

set "hsf_1_dir=%cd%\gdl_bibl\hsf\_ArchiBibl 22"
set "hsf_2_dir=%cd%\gdl_bibl\hsf\_Standart"
set "hsf_3_dir=%cd%\gdl_bibl\hsf\_MEP"

set "bat_dir=%cd%\gdl_bibl\bat"

"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  l2x -l UTF8 "%gdl_1_dir%" "%xml_1_dir%" >"%bat_dir%\_xml_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  l2x -l UTF8 "%gdl_2_dir%" "%xml_2_dir%" >"%bat_dir%\_xml_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  l2x -l UTF8 "%gdl_3_dir%" "%xml_3_dir%" >"%bat_dir%\_xml_log.txt"

cd gdl_bibl
cd lcf
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  createcontainer  archbib25.lcf -compress 9 "%gdl_1_dir%">"%bat_dir%\_lcf_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  createcontainer  standart25.lcf -compress 9 "%gdl_2_dir%">"%bat_dir%\_lcf_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  createcontainer  mep25.lcf -compress 9 "%gdl_3_dir%">"%bat_dir%\_lcf_log.txt"

cd ..
cd hsf
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  l2hsf "%gdl_1_dir%" "%hsf_1_dir%" >"%bat_dir%\_hsf_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  l2hsf "%gdl_2_dir%" "%hsf_2_dir%" >"%bat_dir%\_hsf_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 25\LP_XMLConverter.exe"  l2hsf "%gdl_3_dir%" "%hsf_3_dir%" >"%bat_dir%\_hsf_log.txt"