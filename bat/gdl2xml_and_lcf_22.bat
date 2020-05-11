cd /d %~dp0
cd ..
cd ..
set "gdl_1_dir=%cd%\_ArchiBibl 22"
set "gdl_2_dir=%cd%\_Standart"
set "gdl_3_dir=%cd%\_MEP"
set "xml_1_dir=%cd%\gdl_bibl\xml\_ArchiBibl 22"
set "xml_2_dir=%cd%\gdl_bibl\xml\_Standart"
set "xml_3_dir=%cd%\gdl_bibl\xml\_MEP"

set "bat_dir=%cd%\gdl_bibl\bat"

"C:\Program Files\GRAPHISOFT\ARCHICAD 22\LP_XMLConverter.exe"  l2x -l UTF8 "%gdl_1_dir%" "%xml_1_dir%" >"%bat_dir%\_xml_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 22\LP_XMLConverter.exe"  l2x -l UTF8 "%gdl_2_dir%" "%xml_2_dir%" >"%bat_dir%\_xml_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 22\LP_XMLConverter.exe"  l2x -l UTF8 "%gdl_3_dir%" "%xml_3_dir%" >"%bat_dir%\_xml_log.txt"

cd gdl_bibl
cd lcf
"C:\Program Files\GRAPHISOFT\ARCHICAD 22\LP_XMLConverter.exe"  createcontainer  archbib22.lcf -compress 9 "%gdl_1_dir%">"%bat_dir%\_lcf_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 22\LP_XMLConverter.exe"  createcontainer  standart22.lcf -compress 9 "%gdl_2_dir%">"%bat_dir%\_lcf_log.txt"
"C:\Program Files\GRAPHISOFT\ARCHICAD 22\LP_XMLConverter.exe"  createcontainer  mep22.lcf -compress 9 "%gdl_3_dir%">"%bat_dir%\_lcf_log.txt"