import os


def decodefile(srcfile, from_codec, to_codec):
    trgfile = os.path.abspath(os.path.dirname(
        srcfile)+'\\'+os.path.basename(srcfile)+"_")
    with open(srcfile, 'r', encoding=from_codec) as f, open(trgfile, 'w', encoding=to_codec) as e:
        text = f.read()
        if text.startswith('\ufeff') and to_codec == 'utf-8-sig':
            return
        e.write(text)
    os.remove(srcfile)
    os.rename(trgfile, srcfile)


hsf_path = os.path.abspath(os.path.dirname(
    os.path.dirname(__file__))+'\hsf')

print("Start " + hsf_path)
for address, dirs, files in os.walk(hsf_path):
    for name in files:
        if (name.endswith('.gdl')):
            decodefile(os.path.join(address, name), "utf-8-sig", "utf-8")
print("End " + hsf_path)
