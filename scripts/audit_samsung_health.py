"""Audit lokal read-only. Tidak membuat data final atau mengekspor nilai identitas.

Jalankan dari root proyek: python scripts/audit_samsung_health.py
CSV keluaran berisi metadata audit; JSON dalam sel ditujukan untuk dibaca dengan json.loads.
"""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
import csv
import hashlib
import io
import json
import re

ROOT = Path(__file__).resolve().parents[1]
sources = list(ROOT.glob('samsunghealth_*'))
assert len(sources) == 1, 'Pilih tepat satu direktori ekspor.'
RAW = sources[0]
OUT = ROOT / 'data_audit'
OUT.mkdir(exist_ok=True)
J = lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True)
FILES = sorted(x for x in RAW.rglob('*') if x.is_file())
before = {x: hashlib.sha256(x.read_bytes()).hexdigest() for x in FILES}
tables, inventory, json_objects = {}, [], {}

def dtype(v):
    if v is None or v == '': return 'missing'
    if isinstance(v, bool): return 'boolean'
    if isinstance(v, dict): return 'object'
    if isinstance(v, list): return 'array'
    if isinstance(v, int): return 'integer'
    if isinstance(v, float): return 'float'
    if re.fullmatch(r'[+-]?\d+', str(v)): return 'integer-like string'
    if re.fullmatch(r'[+-]?\d+\.\d+(?:[Ee][+-]?\d+)?', str(v)): return 'float-like string'
    if re.fullmatch(r'\d{4}-\d\d-\d\d(?:[ T].*)?', str(v)): return 'datetime-like string'
    return 'string'

def date_value(key, v):
    # Do not interpret durations, clock targets, IDs or arbitrary numbers as dates.
    if isinstance(v, str) and re.fullmatch(r'\d{4}-\d\d-\d\d(?:[ T].*)?', v):
        try: return datetime.fromisoformat(v).isoformat(sep=' ')
        except ValueError: return None
    if re.search(r'(time|date|timestamp)', key, re.I) and not re.search(r'(duration|offset|latency|goal|weight|score)', key, re.I):
        try:
            n = float(v)
            # Only plausible epoch ranges, explicit heuristic; never silently localize.
            if 946684800000 <= n <= 4102444800000:
                return datetime.fromtimestamp(n/1000, timezone.utc).isoformat()
            if 946684800 <= n <= 4102444800:
                return datetime.fromtimestamp(n, timezone.utc).isoformat()
        except (ValueError, TypeError, OverflowError): pass
    return None

def profile(records, columns):
    types, missing, dates = {}, {}, {}
    for k in columns:
        vs = [r.get(k) for r in records]
        types[k] = dict(Counter(dtype(v) for v in vs))
        missing[k] = sum(v is None or (isinstance(v,str) and not v.strip()) for v in vs)
        ds = [d for v in vs if (d := date_value(k,v))]
        if ds: dates[k] = {'min':min(ds), 'max':max(ds), 'parsed':len(ds)}
    return types, missing, dates

def flatten(obj, prefix='$'):
    out = defaultdict(list)
    def walk(v, k):
        out[k].append(v)
        if isinstance(v,dict):
            for a,b in v.items(): walk(b,k+'.'+a)
        elif isinstance(v,list):
            for b in v: walk(b,k+'[]')
        elif isinstance(v,str) and v.lstrip().startswith(('{','[')):
            try: nested=json.loads(v)
            except (ValueError,TypeError): return
            if isinstance(nested,(dict,list)): walk(nested,k+'{decoded}')
    walk(obj,prefix)
    return out

for f in FILES:
    raw = f.read_bytes()
    encoding = 'utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
    try: text = raw.decode(encoding)
    except UnicodeDecodeError:
        try: encoding='utf-16'; text=raw.decode(encoding)
        except UnicodeError: encoding='cp1252'; text=raw.decode(encoding)
    item = dict(relative_path=f.relative_to(RAW).as_posix(), file_name=f.name,
                extension=f.suffix.lower(), size_bytes=len(raw), sha256=before[f],
                encoding=encoding, physical_lines=len(text.splitlines()), status='ok',
                delimiter='', header_row='', metadata_rows='', row_count='',
                columns_json='[]', dtypes_json='{}', missing_json='{}',
                date_ranges_json='{}', duplicate_rows='', notes='')
    if f.suffix.lower()=='.csv':
        # Detect delimiter per file, not globally. Samsung preamble is checked explicitly.
        candidates=[]
        for delimiter in [',',';','\t','|']:
            parsed=list(csv.reader(io.StringIO(text),delimiter=delimiter))
            candidates.append((max((len(r) for r in parsed[:3]),default=0),delimiter,parsed))
        _, delimiter, parsed=max(candidates,key=lambda x:x[0])
        preamble=bool(parsed and len(parsed[0])==3 and parsed[0][0].startswith('com.samsung.'))
        hi=1 if preamble else 0
        header=parsed[hi] if len(parsed)>hi else []
        rows=parsed[hi+1:]; trailing=0; malformed=0; records=[]
        for row in rows:
            if len(row)==len(header)+1 and row[-1]=='': row=row[:-1];trailing+=1
            if len(row)!=len(header): malformed+=1
            records.append(dict(zip(header,row)))
        types,missing,dates=profile(records,header)
        duplicate=len(records)-len(set(J(r) for r in records))
        entity=re.sub(r'\.\d+\.csv$','',f.name)
        tables[entity]=(header,records,item)
        item.update(delimiter=repr(delimiter),header_row=hi+1,metadata_rows=hi,row_count=len(records),
                    columns_json=J(header),dtypes_json=J(types),missing_json=J(missing),
                    date_ranges_json=J(dates),duplicate_rows=duplicate,
                    notes=f'trailing_empty_field_rows={trailing}; malformed_rows={malformed}; duplicate_header_names={len(header)-len(set(header))}')
        if malformed: item['status']='width_mismatch'
    elif f.suffix.lower()=='.json':
        try:
            obj=json.loads(text);json_objects[f]=obj
            flat=flatten(obj)
            types={k:dict(Counter(dtype(v) for v in vs)) for k,vs in flat.items()}
            missing={k:{'null_or_blank':sum(v is None or (isinstance(v,str) and not v.strip()) for v in vs),'occurrences':len(vs)} for k,vs in flat.items()}
            dates={}
            for k,vs in flat.items():
                ds=[d for v in vs if (d:=date_value(k,v))]
                if ds: dates[k]={'min':min(ds),'max':max(ds),'parsed':len(ds)}
            # Some report JSONs use epoch-ms dates as dictionary keys.
            key_dates=[]
            for k in flat:
                for token in re.findall(r'(?<=\.)(\d{13})(?=\.|$)',k):
                    if d:=date_value('date',token):key_dates.append(d)
            if key_dates:dates['{epoch_ms_dictionary_keys}']={'min':min(key_dates),'max':max(key_dates),'parsed_paths':len(key_dates)}
            records=obj if isinstance(obj,list) else [obj]
            dup=len(records)-len(set(J(r) for r in records))
            absent={}
            if isinstance(obj,list) and all(isinstance(x,dict) for x in obj):
                keys=set().union(*(set(x) for x in obj)) if obj else set()
                absent={k:sum(k not in x for x in obj) for k in sorted(keys)}
            item.update(row_count=len(records),columns_json=J(sorted(flat)),dtypes_json=J(types),missing_json=J(missing),date_ranges_json=J(dates),duplicate_rows=dup,
                        notes=f'root_type={type(obj).__name__}; top_level_absent_keys={J(absent)}; nested missing counts use observed occurrences, not a rectangular table')
        except (json.JSONDecodeError,ValueError):
            item.update(status='empty_json' if not text.strip() else 'invalid_json',notes='Tidak dapat diparse sebagai JSON; tidak diperbaiki.')
    inventory.append(item)

def table(entity): return tables['com.samsung.'+entity][1]
s=table('shealth.sleep'); h=list(s[0]); prefix='com.samsung.health.sleep.'
key=lambda k: prefix+k
starts=[datetime.fromisoformat(r[key('start_time')]) for r in s]
ends=[datetime.fromisoformat(r[key('end_time')]) for r in s]
dur=[(b-a).total_seconds()/60 for a,b in zip(starts,ends)]
overlap=[]
for i in range(len(s)):
    for j in range(i+1,len(s)):
        minutes=(min(ends[i],ends[j])-max(starts[i],starts[j])).total_seconds()/60
        if minutes>0: overlap.append((i,j,minutes))
same_interval=len(s)-len(set(zip(starts,ends)))
duration_pairs=[(i,float(r['sleep_duration']),dur[i]) for i,r in enumerate(s) if r['sleep_duration']]
mismatch=[(i,a,b) for i,a,b in duration_pairs if abs(a-b)>1e-6]
large_mismatch=[(i,a,b) for i,a,b in mismatch if abs(a-b)>=1]
dev=table('health.device_profile')
dev_counts=Counter(); unmatched=0
for r in s:
    matches=[d for d in dev if d['deviceuuid']==r[key('deviceuuid')]]
    if len(matches)==1:dev_counts[matches[0]['model']]+=1
    else:unmatched+=1
watch_file=next(f for f in json_objects if f.name=='sleep.watch_summary.blob_value.json')
watch=json.loads(json_objects[watch_file]['summary_daily_data'])
watch_refs=[r for r in s if r[key('datauuid')]==watch.get('representative_id')]
watch_children=watch.get('summary_data_list',[])
watch_child_matches=sum(any(r[key('datauuid')]==x.get('sleep_uuid') for r in s) for x in watch_children)
watch_linked=[r for r in s if any(r[key('datauuid')]==x.get('sleep_uuid') for x in watch_children)]
awake_dates=Counter(b.date() for b in ends)
span=(max(awake_dates)-min(awake_dates)).days+1
calendar_gaps=span-len(awake_dates)
steps=table('shealth.step_daily_trend');activity=table('shealth.activity.day_summary')
stepdates={datetime.fromisoformat(r['day_time']).date() for r in steps}
actdates={datetime.fromisoformat(r['day_time']).date() for r in activity}
local_awake={ (b+timedelta(hours=7)).date() for b in ends }
refs=Counter(); file_by_name=defaultdict(list)
for f in FILES:file_by_name[f.name].append(f)
for entity,(cols,rs,_) in tables.items():
    for r in rs:
        for col,value in r.items():
            if value and value.endswith('.json'):
                candidates=[f for f in file_by_name[value] if entity in f.parts]
                refs['total']+=1
                refs['resolved_unique' if len(candidates)==1 else 'missing' if not candidates else 'ambiguous']+=1

descriptions={
 'start_time':('Awal interval sesi yang dicatat','timestamp teks tanpa zona eksplisit; offset terpisah','Calon awal sesi; basis UTC perlu konfirmasi'),
 'end_time':('Akhir interval sesi yang dicatat','timestamp teks tanpa zona eksplisit; offset terpisah','Calon waktu bangun; basis UTC perlu konfirmasi'),
 'time_offset':('Offset waktu tersimpan','UTC+0700','Seluruh sesi sama; bukan bukti sendiri bahwa timestamp teks sudah lokal'),
 'datauuid':('ID unik record sesi','string ID','Kunci sesi; jangan dimasukkan laporan publik'),
 'deviceuuid':('Referensi profil perangkat','string ID','Join tepat ke device_profile.deviceuuid'),
 'pkg_name':('Paket aplikasi sumber','string','Paket aplikasi tidak membuktikan metode deteksi tidur'),
 'sleep_duration':('Durasi tersimpan','menit: inferensi dari kesesuaian end-start','Kosong bukan nol; gunakan interval sebagai kandidat durasi terpisah'),
 'goal_bed_time':('Target jam mulai tidur','ms sejak tengah malam: inferensi skala','82800000 setara 23:00; target bukan pengamatan'),
 'goal_wake_up_time':('Target jam bangun','ms sejak tengah malam: inferensi skala','21600000/25200000 setara 06:00/07:00'),
 'sleep_score':('Skor tidur','belum terverifikasi','Seluruh kolom sesi kosong; jangan dipakai sebagai target'),
 'efficiency':('Efisiensi yang diekspor','skala tidak terverifikasi','Semua nol; jangan tafsirkan kualitas buruk'),
 'quality':('Kode kualitas yang diekspor','kode tidak terverifikasi','Semua nol; jangan ditafsirkan ordinal'),
 'has_sleep_data':('Flag ketersediaan data tambahan','kode tidak terverifikasi','Semua nol meskipun interval sesi ada'),
 'create_time':('Waktu pembuatan record','timestamp administratif','Bukan awal tidur'),
 'update_time':('Waktu pembaruan record','timestamp administratif','Bukan waktu pengamatan tidur'),
 'sleep_time':('Nilai target tidur pada sleep_goal','belum pasti; angka berskala ms','Ada nilai negatif; jangan gunakan sebagai durasi aktual'),
 'bed_time':('Target jam tidur pada sleep_goal','dugaan ms sejak tengah malam','Target bukan pengamatan'),
 'wake_up_time':('Target jam bangun pada sleep_goal','dugaan ms sejak tengah malam','Target bukan pengamatan'),
 'set_time':('Waktu perubahan pengaturan target','timestamp administratif','Perlu interval berlaku sebelum join temporal')
}
for name in ['total_sleep_time_weight','latency_weight','deep_weight','rem_weight','wake_weight']:
    descriptions[name]=('Komponen bobot '+name,'skala/rumus tidak diketahui','Tidak digunakan bila kosong; rumus Samsung belum diverifikasi')
for name in ['mental_recovery','physical_recovery','wake_score','deep_score','rem_score','latency_score','nap_score','total_sleep_time_score']:
    descriptions[name]=('Komponen skor atau pemulihan '+name,'skala/rumus tidak diketahui','Jangan merekonstruksi skor tanpa definisi dan input yang valid')
for n in range(1,11):
    descriptions[f'factor_{n:02}']=('Faktor internal pembentuk ringkasan tidur','kode/rumus tidak diketahui','Tidak ada dokumentasi definisi faktor dalam ekspor')
for name in ['total_rem_duration','total_light_duration','sleep_latency','bedtime_detection_delay','wakeup_time_detection_delay']:
    descriptions[name]=('Durasi/latensi terkait '+name,'satuan belum dapat diverifikasi karena kosong','Bukan bukti tersedianya rekaman tahap tidur')
for name in ['integrated_id','combined_id','client_data_id']:
    descriptions[name]=('ID relasi atau sumber '+name,'string ID bila tersedia','Kunci alternatif belum dapat dipakai karena kosong')
for name in ['create_sh_ver','modify_sh_ver','client_data_ver','data_version']:
    descriptions[name]=('Versi aplikasi/data saat pencatatan atau perubahan','kode versi','Metadata provenance, bukan variabel kualitas tidur')
for name in ['original_bed_time','original_wake_up_time','edit_original_start_time','edit_original_end_time']:
    descriptions[name]=('Nilai waktu asli/sebelum perubahan '+name,'representasi waktu belum dapat diverifikasi','Tidak tersedia untuk merekonstruksi riwayat edit bila kosong')
for name in ['original_efficiency','sleep_efficiency_with_latency']:
    descriptions[name]=('Varian efisiensi tidur '+name,'skala/rumus tidak diketahui','Jangan mengganti kolom kosong dengan efficiency konstan nol')
for name in ['sleep_cycle','movement_awakening','is_integrated','sleep_type','stage_analyzed_type']:
    descriptions[name]=('Atribut sesi '+name,'kode/count belum dapat diverifikasi','Makna nilai perlu dokumentasi; tidak dapat dianalisis saat kosong')
for name in ['comment','custom','extra_data']:
    descriptions[name]=('Informasi tambahan sesi '+name,'teks atau payload bila tersedia','Tidak tersedia; nilai bebas berpotensi sensitif')
dictionary=[]
for entity in ['com.samsung.shealth.sleep','com.samsung.shealth.sleep_goal']:
    cols,rs,_=tables[entity]
    for col in cols:
        short=col.removeprefix(prefix);vs=[r[col] for r in rs if r.get(col,'').strip()]
        desc,unit,note=descriptions.get(short,('Field '+short,'tidak dapat dipastikan dari ekspor','Makna kode/rumus belum terverifikasi'))
        if not vs:note='Tidak tersedia: seluruh nilai kosong. '+note
        dictionary.append(dict(source=entity,variable=col,description=desc,observed_type=J(dict(Counter(dtype(v) for v in vs))),unit_or_format=unit,rows=len(rs),non_missing=len(vs),missing=len(rs)-len(vs),unique_non_missing=len(set(vs)),notes=note))
flat=flatten(json_objects[watch_file])
for col,vs in flat.items():
    if '{decoded}' not in col:continue
    dictionary.append(dict(source='preferences/sleep.watch_summary.blob_value.json',variable=col,description='Field cache ringkasan tidur dalam string JSON bertingkat',observed_type=J(dict(Counter(dtype(v) for v in vs))),unit_or_format='epoch ms untuk timestamp bernilai besar; kode lain belum pasti',rows=len(vs),non_missing=sum(v is not None and v!='' for v in vs),missing=sum(v is None or v=='' for v in vs),unique_non_missing=len(set(J(v) for v in vs)),notes='Snapshot preferensi, bukan seri sesi independen. Skor nol/regularity -1 dan binning kosong tidak membuktikan pengukuran fisiologis.'))

# Report blobs are precomputed summaries, not additional sleep sessions.
report_fields=defaultdict(list)
report_docs=0
for f,obj in json_objects.items():
    if 'com.samsung.shealth.report' not in f.parts:continue
    report_docs+=1
    for path,values in flatten(obj).items():
        if 'sleep' not in path.lower():continue
        canonical=re.sub(r'(?<=\.)\d{13}(?=\.|$)','{epoch_ms}',path)
        report_fields[canonical].extend(values)
for path,vs in sorted(report_fields.items()):
    dictionary.append(dict(source='report/*.json (ringkasan aplikasi)',variable=path,description='Field ringkasan tidur yang sudah dihitung aplikasi',observed_type=J(dict(Counter(dtype(v) for v in vs))),unit_or_format='teks presentasi/kode/angka; definisi algoritme belum terverifikasi',rows=len(vs),non_missing=sum(v is not None and v!='' for v in vs),missing=sum(v is None or v=='' for v in vs),unique_non_missing=len(set(J(v) for v in vs)),notes='Bukan sesi tambahan. rows adalah kemunculan path pada seluruh dokumen, bukan jumlah individu. AvgSleepEfficiency=2147483647 menyerupai sentinel; consistency berupa kode belum terdefinisi.'))

def write_csv(name,records):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)

write_csv('inventory.csv',inventory)
write_csv('sleep_data_dictionary.csv',dictionary)

# Integrity: reread every original after audit; no raw file is opened for writing.
after_files=sorted(x for x in RAW.rglob('*') if x.is_file())
assert after_files==FILES,'Daftar file mentah berubah saat audit.'
assert all(hashlib.sha256(f.read_bytes()).hexdigest()==before[f] for f in FILES),'Hash data mentah berubah.'

csv_table=[]
for entity,(cols,rs,item) in tables.items():
    dates=json.loads(item['date_ranges_json'])
    event={k:v for k,v in dates.items() if any(t in k for t in ['start_time','end_time','day_time'])}
    if not event:event=dates
    ranges='; '.join(f"{k}: {v['min']} — {v['max']}" for k,v in event.items()) or 'tidak ditemukan tanggal terparse'
    csv_table.append(f"| `{entity}` | {len(rs)} | {len(cols)} | {ranges} |")
json_groups=Counter(f.relative_to(RAW).parts[1] for f in json_objects)
status=Counter(i['status'] for i in inventory)
nonempty_cols=sum(any(r[c] for r in s) for c in h)
year_counts=Counter(b.year for b in ends)
month_counts=Counter(b.strftime('%Y-%m') for b in ends)
constant={c:next(iter(v)) for c in h if len(v:={r[c] for r in s if r[c]})==1 and not any(x in c for x in ['uuid','pkg_name'])}
dup_content=len(s)-len(set(J({k:v for k,v in r.items() if k not in [key('datauuid'),key('create_time'),key('update_time')]}) for r in s))
report=f'''# Audit dataset Samsung Health — TASK 01

Tanggal audit: 18 November 2026 (Asia/Jakarta). Data kesehatan pribadi; seluruh hasil audit hanya untuk penyimpanan lokal. Identitas akun, nama perangkat personal, UUID, komentar, dan nilai profil pribadi tidak ditampilkan di laporan ini. Nama file pada inventaris menggunakan path relatif terhadap akar ekspor (nama folder akun tidak disalin).

## 1. Lingkup, metode, dan verifikasi

Seluruh {len(FILES):,} file dalam {len(list(RAW.rglob('*')))-len(FILES)} direktori turunan ditelusuri rekursif: {sum(f.suffix=='.csv' for f in FILES)} CSV dan {sum(f.suffix=='.json' for f in FILES):,} JSON; total {sum(f.stat().st_size for f in FILES):,} byte. Tidak ditemukan ekstensi lain atau berkas dokumentasi skema terpisah. Semua file dibaca, bukan sampling. Hash SHA-256 sebelum dan sesudah pemeriksaan cocok untuk seluruh file; daftar file juga tetap. Ini membuktikan isi file tidak berubah selama audit ini, bukan validasi akurasi sensor.

Inventaris mencatat ukuran, hash, encoding, baris fisik, baris data/logical record, header, delimiter, seluruh kolom/path JSON, tipe teramati, missing, duplikasi dalam file, dan rentang tanggal per variabel. Nama kolom asli dipertahankan. Tipe CSV merupakan inferensi isi teks, bukan deklarasi skema Samsung. Tidak ada data yang digabung menjadi dataset analisis, diimputasi, dihapus, atau diagregasi untuk menghasilkan dataset final. Hitungan per bulan/hari di laporan hanya diagnostik cakupan audit.

Encoding teramati: {J(dict(Counter(i['encoding'] for i in inventory)))}. Status parse: {J(dict(status))}. CSV diuji per file dengan kandidat delimiter koma, titik koma, tab, dan pipe; seluruhnya memilih koma. Baris pertama seluruh CSV merupakan preamble tiga field (jenis entitas dan dua angka metadata yang semantiknya belum diverifikasi); header pada baris kedua. Baris data memiliki satu field kosong tambahan di ujung; field terminal ini ditoleransi hanya saat kosong, tanpa menggeser header. Jumlah baris data tidak menghitung preamble/header. Tidak menggunakan `on_bad_lines=skip`.

JSON diparse sesuai tipe akar: dict merupakan satu dokumen, list dihitung per elemen, scalar satu nilai. String yang berisi object/list JSON didekode lagi untuk memeriksa struktur bertingkat. Satu JSON kosong pada entitas `heart_health_score` tidak dapat diparse, bukan bukti tersedianya skor jantung. Untuk JSON, `missing_json` mencatat null/string kosong dan jumlah kemunculan per path; ketidakhadiran key tingkat teratas list-of-object dicatat terpisah di `notes`. Path nested yang tidak muncul bukan otomatis nol; metrik nested bukan persentase missing tabel persegi. Array kosong tetap array kosong. Rentang tanggal dibaca dari teks ISO atau kandidat epoch detik/ms tahun 2000–2100 berdasarkan nama field; tanggal tersimpan tanpa zona tetap tanpa zona, epoch ditampilkan UTC. Field target/jam/durasi tidak disulap menjadi tanggal kalender.

Duplikasi dihitung sebagai kemunculan tambahan record identik dalam tiap CSV/array JSON. Tidak ditemukan duplikasi baris identik di seluruh CSV. Kesamaan isi file lain tidak otomatis duplikasi sesi: ada {sum(n>1 for n in Counter(i['sha256'] for i in inventory if i['extension']=='.json').values())} kelompok JSON dengan hash byte-identik yang memang dapat direferensikan record berbeda. SHA-256 memungkinkan identifikasi file byte-identik; jangan menghapusnya tanpa memeriksa referensi. Sel metadata inventaris terbesar melebihi batas default modul csv Python; pembacaan ulang dengan csv.reader memerlukan `csv.field_size_limit(100_000_000)`; pandas.read_csv juga dapat digunakan. File inventaris bukan tabel data kesehatan final.

## 2. Inventaris entitas CSV

| Entitas | Baris | Kolom | Rentang tanggal teramati (basis asli, belum dilokalkan) |
| --- | ---: | ---: | --- |
{chr(10).join(csv_table)}

JSON valid menurut folder entitas: `{J(dict(json_groups))}`. Seluruh path file, termasuk file JSON kosong, ada pada `inventory.csv`.

## 3. Temuan sesi tidur

- Tabel `sleep`: **{len(s)} baris, {len(h)} kolom**, {nonempty_cols} kolom pernah terisi dan {len(h)-nonempty_cols} kolom seluruhnya kosong. ID `datauuid` terisi dan unik {len(set(r[key('datauuid')] for r in s))} dari {len(s)}. `client_data_id`, `integrated_id`, dan `combined_id` kosong sehingga tidak tersedia sebagai kunci integrasi alternatif.
- Awal sesi tersimpan: **{min(starts)} sampai {max(starts)}**. Akhir sesi: **{min(ends)} sampai {max(ends)}**. Rentang ini adalah timestamp teks ekspor, bukan klaim waktu lokal final. Jumlah sesi menurut tahun akhir sesi: `{J(dict(year_counts))}`.
- Offset: `{J(dict(Counter(r[key('time_offset')] for r in s)))}`. Semua timestamp awal/akhir dapat diparse; tidak mengandung suffix zona. Jangan langsung memberi zona Asia/Jakarta atau menambah tujuh jam dua kali.
- Durasi interval `end-start`: **{min(dur):g}–{max(dur):g} menit**; interval nol/negatif: **{sum(d<=0 for d in dur)}**. `sleep_duration` terisi **{len(duration_pairs)}**, kosong **{len(s)-len(duration_pairs)}**. Dengan kandidat satuan menit, selisih terhadap interval pada nilai terisi: **{len(mismatch)}** baris, semuanya di bawah satu menit; ketidaksesuaian minimal satu menit: **{len(large_mismatch)}**. Selisih detik absolut: `{J([round(abs(a-b)*60,3) for _,a,b in mismatch])}`. Ketiganya konsisten dengan penyimpanan durasi menit bulat ketika timestamp mempunyai detik/milidetik; tidak langsung dianggap kesalahan. Satuan menit didukung kecocokan empiris, bukan dokumentasi resmi. Baris di luar rentang 180–720 menit: **{sum(d<180 or d>720 for d in dur)}**; batas ini hanya penanda pemeriksaan, bukan diagnosis atau aturan penghapusan.
- Duplikasi semua field: **{tables['com.samsung.shealth.sleep'][2]['duplicate_rows']}**. Duplikasi interval start/end: **{same_interval}** kemunculan tambahan. Duplikasi isi setelah mengabaikan ID serta create/update: **{dup_content}** kemunculan tambahan. Pasangan interval dengan overlap positif: **{len(overlap)}**, melibatkan **{len(set(i for a,b,_ in overlap for i in (a,b)))}** record; jumlah menit overlap per pasangan **{sum(x[2] for x in overlap):g}** (bukan total union). Tidak menjumlahkan durasi sesi sebelum konflik ini diselesaikan.
- Tanggal akhir sesi unik pada basis teks: **{len(awake_dates)}** dalam rentang **{span}** hari; **{calendar_gaps}** tanggal tanpa catatan tidur dan **{sum(n>1 for n in awake_dates.values())}** tanggal dengan lebih dari satu record. Ketiadaan record bukan bukti tidak tidur. Ini belum pemilihan sesi utama atau penggabungan tidur siang.
- Cakupan bulanan (jumlah record menurut akhir sesi, bukan malam independen): `{J(dict(sorted(month_counts.items())))}`.

### 3.1 Ketersediaan kualitas, stage, dan cache

Kolom `sleep_score`, `nap_score`, `deep_score`, `rem_score`, `total_rem_duration`, `total_light_duration`, `sleep_cycle`, `stage_analyzed_type`, latency, faktor kualitas, dan recovery seluruhnya kosong. `has_sleep_data=0`, `quality=0`, dan `efficiency=0.0` pada semua {len(s)} record. Tidak ada tabel/file entitas sleep-stage atau deret label tahap tidur yang ditemukan pada struktur/path JSON yang diaudit. Dengan demikian, analisis REM/deep/light, sleep efficiency valid, maupun pemodelan sleep score **belum didukung** ekspor ini.

Ada satu blob preferensi bernama `sleep.watch_summary.blob_value.json`. Field `summary_daily_data` merupakan string JSON yang telah didekode dan diperiksa. Berisi satu snapshot ringkasan, `sleep_score=0`, `yesterday_sleep_score=0`, `sleep_regularity=-1`, satu elemen `summary_data_list`, dan array binning fisiologis yang kosong. `heart_rate_data.max_hr=300` disertai `hr=0` dan timestamp nol; bukan hasil pengukuran yang layak dianalisis. `representative_id` cocok dengan **{len(watch_refs)}** record sleep; `sleep_uuid` elemen ringkasan cocok sebanyak **{watch_child_matches}**. Karena itu cache tidak boleh ditambahkan sebagai sesi baru atau diperlakukan sebagai seri sleep score. Nama “watch” pada preferensi tidak membuktikan adanya pengukuran dari jam.

Selain itu, **{report_docs} JSON report** memuat field tidur yang telah diringkas aplikasi: `averageSleepTime` berupa teks, `sleepConsistencyDataList` berupa pemetaan key epoch-ms ke kode, serta `AvgSleepEfficiency` bernilai **2147483647 pada seluruh report** (menyerupai sentinel batas integer, bukan efisiensi valid). Terdapat juga label unit dan request tracker. Kode consistency belum memiliki definisi terverifikasi dan muncul lagi dalam struktur ringkasan internal, sehingga tidak boleh dijumlahkan sebagai observasi baru. Metadata ini masuk kamus data dan inventaris; bukan sleep-stage dan tidak menggantikan sesi mentah. Tidak ada path JSON dengan nama stage/deep/rem_duration/rem_score yang ditemukan dalam pemeriksaan skema menyeluruh.

### 3.2 Sumber perangkat dan basis waktu

Join nilai `sleep.deviceuuid` ke `device_profile.deviceuuid` menghasilkan `{J(dict(dev_counts))}`; record tanpa tepat satu profil: **{unmatched}**. Model SM-A556E konsisten dengan smartphone Samsung seri A; profil lain berlabel agregasi `Combined` dan `all_target`, bukan bukti smartwatch. Paket semua sesi ialah `com.sec.android.app.shealth`. Kesimpulan terbatas: sumber pencatatan yang dapat ditautkan adalah profil ponsel. Tidak ada bukti sensor smartwatch yang terverifikasi. Ekspor tidak cukup untuk membedakan input manual, estimasi ponsel, atau data yang pernah disinkronkan.

Timestamp epoch pada `movement_data` cache dapat dibandingkan terhadap teks awal/akhir sesi rujukan (hasil pengujian tambahan dicatat di bawah). Walaupun satu kecocokan mendukung hipotesis teks UTC, kebijakan zona waktu final perlu dicocokkan dengan satu sesi pada aplikasi Samsung Health. Sasaran pengaturan jam tidur berada pada skala ms sejak tengah malam dan tidak otomatis menggunakan aturan timestamp epoch.

## 4. Hubungan antarfile dan variabel pendamping

Unit kandidat primer adalah **satu sesi tidur** dengan ID record unik. Untuk pertanyaan “per malam”, unit baru ditetapkan setelah aturan sesi utama, tidur siang, lintas tengah malam, dan overlap disepakati; gunakan tanggal bangun lokal sebagai kandidat tanggal atribusi dan simpan tanggal mulai pula.

Hubungan yang diperiksa:

1. `sleep.deviceuuid → device_profile.deviceuuid`: identitas sumber, bukan join berdasarkan nama perangkat.
2. `sleep.datauuid → preferences.summary_daily_data.representative_id / summary_data_list.sleep_uuid`: cache ringkasan menunjuk record, bukan observasi baru.
3. `sleep_goal`: {len(table('shealth.sleep_goal'))} record riwayat target. Tidak memiliki foreign key sesi langsung; `set_time` adalah calon dasar as-of join setelah basis waktu dan masa berlaku ditentukan. Nilai `sleep_time`: `{J(dict(Counter(r['sleep_time'] for r in table('shealth.sleep_goal'))))}`; nilai negatif tidak boleh dipakai sebagai durasi tidur aktual.
4. Field CSV yang berisi nama `.json` diperiksa terhadap basename dan folder entitas yang sama: `{J(dict(refs))}`. Referensi kosong tidak diasumsikan memiliki blob. JSON yang tidak direferensikan bisa berupa metadata/cache dan tidak otomatis record yatim bermasalah.
5. Aktivitas harian: `activity.day_summary` mempunyai {len(activity)} record dan {len(actdates)} tanggal unik; variabel yang tersedia meliputi `step_count`, `active_time`, `exercise_time`, `distance`, `calorie`, `walk_time`, `run_time`, `longest_idle_time`. Makna satuan tiap durasi/energi perlu diperiksa sebelum dipakai; count langkah adalah kandidat paling langsung.
6. `step_daily_trend`: {len(steps)} record untuk {len(stepdates)} tanggal, `source_type` `{J(dict(Counter(r['source_type'] for r in steps)))}`. `tracker.pedometer_day_summary` juga menyediakan beberapa record per tanggal. Jangan menjumlahkan sumber gabungan dan sumber ponsel; kode sumber perlu dipetakan sebelum memilih seri kanonis. Jangan join dua tabel multibaris lewat tanggal karena dapat membentuk many-to-many.
7. Potensi cakupan tanggal tidur dengan langkah: {len(set(awake_dates)&stepdates)} tanggal pada basis teks, atau {len(local_awake&stepdates)} tanggal jika teks UTC ditambah offset +07. Dengan aktivitas harian: {len(set(awake_dates)&actdates)} dan {len(local_awake&actdates)} tanggal berturut-turut. Ini hanya perbandingan himpunan tanggal, bukan hasil join final atau sampel independen. Aktivitas hari sebelum tidur versus hari setelah bangun harus dibedakan sesuai arah pertanyaan.
8. `exercise`, `water_intake`, dan `weight` tersedia sebagai kandidat tambahan, namun cakupannya lebih jarang (lihat tabel). Siklus, profil pengguna, sosial, dan preferensi mengandung konteks sensitif; tidak diperlukan untuk fokus awal tidur dan tidak diprioritaskan.

## 5. Rencana cleaning dan integrasi (belum dijalankan)

1. Pertahankan ekspor read-only dan hash provenance. Baca setiap entitas dengan parser sesuai preamble/header dan trailing field. Simpan nilai asli serta baris sumber untuk penelusuran lokal; ID pribadi diganti token hanya jika dataset analisis nanti dibuat.
2. Parse timestamp tanpa menimpa teks asli. Verifikasi satu contoh di aplikasi untuk menetapkan apakah teks ekspor UTC; bandingkan cache epoch dan offset. Setelah jelas, buat waktu UTC dan lokal secara terpisah. Validasi tanggal baru, perubahan offset, lintas hari, dan tanggal pengumpulan parsial.
3. Validasi ID dan interval. Tandai seluruh pasangan overlap, interval identik, durasi ekstrem, dan sesi lebih dari satu per tanggal. Tinjau provenance/waktu update sebelum menentukan record versi terbaru atau representasi kanonis. Jangan otomatis menghapus record dengan interval sama; gunakan aturan deterministik setelah inspeksi. Jika interval memang merupakan bagian satu sesi, hitung union interval hanya setelah alasan penggabungan terbukti.
4. Simpan `sleep_duration` asli; nilai kosong tetap missing. Buat calon `interval_duration_minutes` dari timestamp yang valid dengan label “durasi interval tercatat”, bukan total waktu fisiologis tertidur. Kecocokan nilai terisi mendukung menit. Selisih, jika muncul, diberi flag dan ditinjau; tidak ditimpa diam-diam.
5. Kolom seluruhnya kosong ditandai unavailable. `quality`, `efficiency`, dan flag konstan tidak dipakai sebagai ukuran kualitas. Cache skor nol dan regularity -1 dikeluarkan dari fitur kualitas sampai semantiknya terverifikasi, tanpa mengganti data mentah. Missing durasi/aktivitas tidak diisi nol atau rata-rata.
6. Setelah konflik sesi selesai, tetapkan unit sesi atau malam. Untuk unit malam, dokumentasikan aturan sesi utama dan tidur siang serta tanggal bangun lokal. Hitung coverage/gap dan frekuensi missing terlebih dahulu; jangan interpolasi malam tanpa catatan sebagai tidur normal.
7. Pilih satu sumber langkah/aktivitas harian dengan pemeriksaan kesesuaian source/device dan konflik antartabel. Pastikan tepat satu record kanonis per hari sebelum join. Lakukan join berarah waktu (aktivitas sebelum tidur → sesi berikutnya) dengan validasi cardinality dan jumlah unmatched. Jangan menjumlahkan metrik yang merepresentasikan hal yang sama.
8. Tangani outlier melalui flag dan analisis sensitivitas yang mempertahankan hasil dengan/ tanpa record yang terbukti bermasalah. Jangan hapus berdasarkan IQR saja. Catat bias perubahan perangkat/aplikasi dan pencatatan manual.
9. Jika pemodelan dipilih, split kronologis, baseline sederhana, fitur lag hanya dari masa lalu, dan evaluasi rolling. Transformasi/imputasi yang memang dibenarkan dipelajari hanya pada data latih. Finalisasi sampel efektif setelah cleaning, bukan dari 653 baris mentah.

## 6. Rekomendasi topik UAS

### A. Pola dan keteraturan jadwal tidur pribadi — prioritas utama

- **Business Understanding:** menyediakan refleksi kebiasaan tidur untuk membantu perencanaan rutinitas harian pribadi.
- **Rumusan dan tujuan:** bagaimana variasi jam mulai, jam bangun, serta durasi interval tidur sepanjang waktu dan antara hari kerja/akhir pekan? Tujuan: memetakan pola, pergeseran jadwal, dan kestabilan pencatatan.
- **Sumber/pengumpulan:** ekspor Samsung Health lokal pada 18 November 2026; sesi ditautkan ke profil ponsel. Metode perekaman asli manual/otomatis belum pasti. Gunakan sleep, offset, dan target hanya bila riwayat berlakunya terverifikasi.
- **Variabel:** awal/akhir lokal tervalidasi, durasi interval, tanggal bangun, hari dalam minggu, bulan, flag overlap/missing, serta target jadwal opsional.
- **Metode:** EDA longitudinal, kalender cakupan, distribusi dan median/IQR durasi, statistik sirkular jam tidur, rolling median, perbandingan hari kerja/akhir pekan dengan interval ketidakpastian berbasis blok bila diperlukan. Bisa dikerjakan memakai pandas, matplotlib/seaborn, scipy di Colab. Tidak memerlukan Machine Learning agar tetap menjadi analisis data yang bermakna.
- **Keterbatasan:** satu individu, interval tercatat bukan validasi tidur fisiologis, sesi overlap/gap, belum ada stage/score valid, dan akhir pekan tidak selalu sama dengan hari libur aktual.

### B. Hubungan aktivitas fisik harian dengan durasi dan jadwal tidur

- **Business Understanding:** memahami apakah rutinitas aktivitas berjalan bersamaan dengan perubahan tidur untuk mendukung evaluasi kebiasaan pribadi.
- **Rumusan dan tujuan:** apakah jumlah langkah pada hari sebelum tidur berhubungan dengan durasi dan jam mulai sesi berikutnya, setelah mempertimbangkan pola mingguan?
- **Sumber/pengumpulan:** ekspor yang sama; sleep dan satu seri kanonis langkah dari activity.day_summary atau step_daily_trend. Proses: validasi sumber, satu baris per hari, lalu join temporal terarah; tidak menggabungkan semua CSV.
- **Variabel:** langkah, hari dalam minggu, tren waktu, durasi interval tidur, jam mulai dengan representasi sirkular; durasi aktivitas opsional setelah satuan diverifikasi.
- **Metode:** scatter/lag plot, korelasi Spearman, regresi sederhana dengan kontrol hari/tren, atau GAM bila diperlukan; gunakan bootstrap blok/residual yang mempertimbangkan dependensi waktu. Laporkan sensitivitas pemilihan sumber dan gap. Python Colab mencukupi.
- **Keterbatasan:** hubungan observasional bukan sebab-akibat; tidak ada kontrol lengkap untuk stres, kafein, pekerjaan, atau pemakaian perangkat. Tanggal beririsan belum menjamin kualitas pencatatan maupun jumlah sampel final. Multiple-source langkah berisiko hitung ganda.

### C. Estimasi durasi interval tidur berikutnya dari riwayat pribadi — bersyarat

- **Business Understanding:** menilai apakah riwayat tidur pribadi mempunyai pola yang cukup stabil untuk membuat perkiraan perencanaan sesi berikutnya.
- **Rumusan dan tujuan:** apakah baseline riwayat terbaru dapat ditingkatkan dengan hari dalam minggu dan fitur lag yang tersedia sebelum sesi dimulai? Target berupa durasi interval berikutnya, bukan sleep score.
- **Sumber/pengumpulan:** seri sesi/malam kanonis dari ekspor sleep setelah cleaning yang disetujui; langkah hari sebelumnya opsional jika benar-benar tersedia saat prediksi.
- **Variabel:** durasi sesi terdahulu, jeda antarcatatan, hari dalam minggu, rolling median masa lalu; langkah lag opsional. Tidak menggunakan jam akhir aktual sesi target atau target-derived feature.
- **Metode:** baseline nilai terakhir/median bergerak, Ridge sebagai model utama, pembanding pohon sederhana bila sampel efektif memadai. Split waktu dan rolling-origin; evaluasi MAE menit dan bandingkan dengan baseline. Jangan memakai random split atau menganggap gap sebagai observasi harian penuh.
- **Keterbatasan:** hanya {len(s)} record awal dengan ketergantungan waktu, gap, overlap, serta perubahan pola; jumlah efektif berkurang setelah pemeriksaan. Nilai prediksi tidak berlaku bagi populasi atau untuk diagnosis. Pilih topik A bila seri tidak cukup stabil setelah cleaning.

## 7. Keamanan, berkas keluaran, dan batas pekerjaan

`.gitignore` mengabaikan ekspor `samsunghealth_*/`, seluruh `data_audit/`, direktori data mentah/cleaning, keluaran, dan format data umum. Audit juga sensitif karena memuat tanggal, struktur, nama file/UUID, dan hash; jangan unggah hasil ini tanpa sanitasi. Aturan ignore tidak menghapus file yang sudah pernah terlacak Git. Saat diperiksa, direktori proyek belum merupakan repository Git (`git rev-parse --show-toplevel` gagal karena tidak ada repository), sehingga status tracked tidak berlaku saat ini. Aturan ignore diperiksa dengan Git pada repository sementara tanpa menginisialisasi repository proyek. Tidak ada commit/push/deploy.

Keluaran: `inventory.csv`, `sleep_data_dictionary.csv`, dan laporan ini. CSV UTF-8 dengan BOM dan delimiter koma; sel berakhiran `_json` memuat metadata JSON. Skrip `scripts/audit_samsung_health.py` memungkinkan audit diulang secara lokal; tidak menyimpan identitas akun dalam kode. Tidak dibuat dataset final, notebook ML, cleaning, atau laporan UAS. Verifikasi runtime perangkat/sensor dan tampilan aplikasi belum dilakukan.
'''

# Independent comparison of cache epoch against referenced session text.
if watch_linked and watch_children:
    rr=watch_linked[0];mv=watch_children[0].get('movement_data',{})
    comparisons={}
    for field in ['start_time','end_time']:
        epoch=mv.get(field)
        if epoch:
            epoch_dt=datetime.fromtimestamp(epoch/1000,timezone.utc).replace(tzinfo=None)
            comparisons[field]=(datetime.fromisoformat(rr[key(field)])-epoch_dt).total_seconds()/3600
    report+='\n## 8. Pengujian tambahan basis waktu\n\n'
    report+=f'Selisih timestamp teks sesi rujukan dikurangi UTC dari epoch cache (jam): `{J(comparisons)}`. '
    report+='Selisih nol mendukung hipotesis timestamp teks UTC pada snapshot ini; bukti satu snapshot tidak menetapkan seluruh histori secara definitif. Tetap perlu konfirmasi tampilan aplikasi sebelum cleaning zona waktu.\n'

(OUT/'audit_report.md').write_text(report,encoding='utf-8')
print(J({'files':len(FILES),'bytes':sum(f.stat().st_size for f in FILES),'parse_status':dict(status),'sleep_rows':len(s),'sleep_columns':len(h),'all_missing_columns':len(h)-nonempty_cols,'duration_min':min(dur),'duration_max':max(dur),'duration_nonmissing':len(duration_pairs),'duration_mismatches':len(mismatch),'overlap_pairs':len(overlap),'duplicate_intervals':same_interval,'dates_with_sleep':len(awake_dates),'calendar_gaps':calendar_gaps,'device_models':dict(dev_counts),'references':dict(refs),'raw_hash_verification':'all unchanged','dictionary_rows':len(dictionary)}))
