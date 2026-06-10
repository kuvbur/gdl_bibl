import csv

output_file = 'sort2code.txt'

data_list = []
data_list.append('"get_br":')
data_list.append("j=0")
with open("перемычки.txt", mode='r', encoding='cp1251') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        if "-п" not in row[0]:
            data_list.append("j=j+1")
            data_list.append(f'    naen_m_br[j]="{row[0]}"')
            data_list.append(f"    dlin_m_br[j]={row[1]}/1000")
            data_list.append(f"    tolsh_m_br[j]={row[2]}/1000")
            data_list.append(f"    vis_m_br[j]={row[3]}/1000")
            data_list.append("    max_pr_m_br[j]=0")
            data_list.append(f"    nagr_m_br[j]={row[4]}")
            data_list.append(f"    ves_m_br[j]={row[5]}")
            data_list.append('    gost_m_br[j] = "ГОСТ 948-2016"')
data_list.append('return')

data_list.append('"get_fb":')
data_list.append("j=0")
with open("перемычки фибробетон.txt", mode='r', encoding='cp1251') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        data_list.append("j=j+1")
        data_list.append(f'    naen_m_fb[j]="{row[0]}"')
        data_list.append(f"    dlin_m_fb[j]={row[1]}/1000")
        data_list.append(f"    tolsh_m_fb[j]={row[2]}/1000")
        data_list.append(f"    vis_m_fb[j]={row[3]}/1000")
        data_list.append(f"    nagr_m_fb[j]={row[4]}")
        data_list.append(f"    ves_m_fb[j]={row[5]}")
        data_list.append(f"    max_pr_m_fb[j]={row[6]}/1000")
        data_list.append(f'    gost_m_fb[j]="ТУ 5828-002-80392712-2015"')
data_list.append('return')

data_list.append('"get_ug":')
data_list.append("j=0")
with open("перемычки уголки.txt", mode='r', encoding='cp1251') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        data_list.append("j=j+1")
        data_list.append(f'    naen_m_ug[j]="{row[0]}"')
        data_list.append(f"    ves_m_ug[j]={row[1]}")
        data_list.append(f"    b_ug[j]={row[2]}/1000")
        data_list.append(f"    h_ug[j]={row[3]}/1000")
        data_list.append(f"    t_ug[j]={row[4]}/1000")
        data_list.append(f'    gost_ug[j]="{row[5]}"')
data_list.append('return')


with open(output_file, mode='w', encoding='utf-8') as f:
    for row in data_list:
        f.write(row + '\n')