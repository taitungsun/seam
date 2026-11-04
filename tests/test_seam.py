"""SEAM 自動測試（Playwright + Chromium，以 file:// 開啟）。
用法：python -I tests/test_seam.py [SEAM_vX.Y.html]   （預設取 repo 裡版本號最大的主程式）
測試資料一律虛構。"""
import json, pathlib, re, sys, tempfile
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
def newest():
    ver = lambda f: tuple(int(x) for x in re.findall(r'\d+', f.stem))
    return max(ROOT.glob('SEAM_v*.html'), key=ver)
HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else newest()
URL = HTML.as_uri()

results = []
def ok(name, cond, detail=''):
    results.append((bool(cond), name, detail))

ADD_STUDENT = """(name) => { DATA.students.push({ id: uid('s'), name, class: '資一甲', seat: '1', studentId: 'T' + Math.random().toString().slice(2, 8),
    status: '在學', category: '學習障礙' }); migrateData(); scheduleSave(); renderCurrentTab(); }"""

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(accept_downloads=True)
    external = []
    ctx.route(re.compile(r'^https?://'), lambda r: (external.append(r.request.url), r.abort()))
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    msgs = []
    def dlg(d):
        msgs.append((d.type, d.message)); d.accept()
    pg.on('dialog', dlg)
    pg.goto(URL); pg.wait_for_load_state('load')
    toast = lambda: pg.inner_text('#toast').strip()

    ver = pg.evaluate('APP_VERSION')
    ok('版本號與檔名一致', ver in HTML.name.replace('_', ''), ver)
    html = HTML.read_text(encoding='utf-8')
    ok('沒有 Google 字型', 'googleapis' not in html and 'gstatic' not in html)
    ok('分頁名稱「特教行政管理系統 SEAM」', pg.title() == '特教行政管理系統 SEAM', pg.title())
    nav = pg.locator('.nav-item').all_inner_texts()
    ok('側欄：總覽…系統設定', [t.splitlines()[-1].strip() for t in nav] == ['總覽', '學生資料', '分組課表', '成績管理', '經費管理', '系統設定'], nav)

    # 各頁沒有英文小標、沒有 JS 錯誤
    eng = []
    for t in ['dashboard', 'students', 'schedule', 'grades', 'budget', 'settings']:
        pg.evaluate(f"setTab('{t}')")
        eng += [x for x in pg.locator('.eyebrow').all_inner_texts() if re.fullmatch(r'[A-Za-z ]+', x.strip())]
    ok('沒有英文小標', not eng, eng)

    # 設定頁用詞與按鈕
    pg.evaluate("setTab('settings')")
    heads = [h.strip() for h in pg.locator('#content .panel-head h3').all_inner_texts()]
    ok('區塊「學校資訊」「備份與還原」', '學校資訊' in heads and '備份與還原' in heads, heads)
    ok('按鈕「儲存設定」', pg.locator('#content button:text-is("儲存設定")').count() == 1)
    row = pg.locator('#content .panel:has(h3:text-is("備份與還原")) button')
    labels = [x.strip() for x in row.all_inner_texts()]
    ok('備份區按鈕順序', labels == ['下載備份', '還原備份', '清除資料'], labels)
    cls = row.evaluate_all('bs => bs.map(b => b.className)')
    ok('按鈕樣式：主要、一般、危險', cls == ['btn btn-primary', 'btn', 'btn btn-danger'], cls)
    pg.click('#content button:text-is("儲存設定")')
    ok('儲存設定提示', toast() == '已儲存設定', toast())

    # 新增測試學生
    pg.evaluate(ADD_STUDENT, '測試甲'); pg.evaluate(ADD_STUDENT, '測試乙')
    pg.wait_for_timeout(500)
    ok('兩位測試學生', pg.evaluate('DATA.students.length') >= 2)

    # 關閉頁面不跳出提醒，且延遲寫入的修改不遺失
    n_before = len(msgs)
    pg.evaluate(ADD_STUDENT, '測試丙')        # 0.35 秒後才寫入；立刻重新載入
    pg.reload(); pg.wait_for_load_state('load')
    ok('重新載入時沒有「要離開網站嗎？」', not any(t == 'beforeunload' for t, _ in msgs[n_before:]), msgs[n_before:])
    ok('最後一筆修改沒有遺失', '測試丙' in pg.evaluate('DATA.students.map(s => s.name)'))
    count = pg.evaluate('DATA.students.length')

    # 下載備份
    pg.evaluate("setTab('settings')")
    with pg.expect_download() as dl:
        pg.click('#content button:text-is("下載備份")')
    path = dl.value.path(); data = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    ok('備份檔名', re.fullmatch(r'SEAM_\d{10}\.json', dl.value.suggested_filename), dl.value.suggested_filename)
    ok('備份最外層 app/version/exportedAt', data.get('app') == 'SEAM' and data.get('version') == ver and 'exportedAt' in data)
    ok('下載後提示「已下載備份檔」', toast() == '已下載備份檔', toast())

    # 清除資料：問兩次
    n_before = len(msgs)
    pg.click('#content button:text-is("清除資料")')
    got = [m for _, m in msgs[n_before:]]
    ok('清除資料問兩次', got == ['確定要清除資料嗎？此動作無法復原，請先下載備份。', '再確認一次：真的要清除所有資料嗎？'], got)
    ok('清除後提示', toast() == '已清除資料', toast())

    # 還原備份
    n_before = len(msgs)
    pg.set_input_files('#import-file', path)
    pg.wait_for_function(f'DATA.students.length === {count}')
    got = [m for _, m in msgs[n_before:]]
    ok('還原確認文字', any(re.match(r'目前 \d+ 位學生，備份檔 \d+ 位學生。還原會取代目前所有資料，確定要還原嗎？', m) for m in got), got)
    pg.wait_for_timeout(200)
    ok('還原後提示「已還原備份」', toast() == '已還原備份', toast())

    # 擋下其他系統的備份
    tmp = pathlib.Path(tempfile.mkdtemp())
    for app, body in [('IST', {'app': 'IST', 'version': 'v1.7', 'records': [], 'settings': {}}),
                      ('SEIA', {'app': 'SEIA', 'version': 'beta', 'v': 1, 'cases': []})]:
        f = tmp / f'{app}.json'; f.write_text(json.dumps(body), encoding='utf-8')
        pg.set_input_files('#import-file', str(f)); pg.wait_for_timeout(300)
        ok(f'擋下 {app} 備份', toast() == f'這是 {app} 的備份檔，請在 {app} 還原，目前資料未變動'
           and pg.evaluate('DATA.students.length') == count, toast())

    # 提示訊息不加 ✓、確認視窗用字
    ok('程式中的提示訊息沒有 ✓ 開頭', not re.search(r"showToast\(['`]✓", html))
    ok('沒有「記錄」名詞誤用（成績記錄、尚無記錄）', '成績記錄' not in html and '尚無記錄' not in html)

    # 狀態列與 7 天備份提醒（規範 11.1、13.3）
    pill = lambda: pg.inner_text('#savepill')
    banner = lambda: pg.locator('#backup-banner').is_visible()
    ok('側欄不再顯示上次備份', pg.locator('#backup-status').count() == 0)
    ok('狀態列不加 role=status', pg.get_attribute('#savepill', 'role') is None)
    box = pg.locator('#savepill').bounding_box(); vp = pg.viewport_size
    ok('狀態列固定在畫面右下角', pg.evaluate("getComputedStyle(document.getElementById('savepill')).position") == 'fixed'
       and box and vp['width'] - (box['x'] + box['width']) < 40 and vp['height'] - (box['y'] + box['height']) < 40, box)
    ok('狀態列有「儲存」「備份」按鈕', pg.locator('#savepill button').all_inner_texts() == ['儲存', '備份'])
    def set_backup(days_ago):
        pg.evaluate(f"DATA.meta.lastBackupAt = new Date(Date.now() - {days_ago} * 86400000).toISOString(); updateBackupStatus()")
    set_backup(6)
    ok('6 天：不逾期、不顯示提醒', '已逾' not in pill() and not banner(), pill())
    roc = pg.evaluate("fmtDateTime(DATA.meta.lastBackupAt).split(' ')[0]")
    ok('上次備份以民國年顯示', re.fullmatch(r'1\d\d/\d\d/\d\d', roc) and f'上次備份 {roc}' in pill(), pill())
    set_backup(8)
    ok('8 天：狀態列標示「已逾 7 天」', '（已逾 7 天）' in pill(), pill())
    ok('8 天：頁面上方提醒', banner() and '已 8 天未備份' in pg.inner_text('#backup-banner-text'), pg.inner_text('#backup-banner-text'))
    pg.evaluate("delete DATA.meta.lastBackupAt; updateBackupStatus()")
    ok('從未備份：「尚未備份」與頁面上方提醒', '｜尚未備份' in pill() and banner(), pill())
    with pg.expect_download():
        pg.click('#backup-banner button:text-is("立即備份")')
    ok('按「立即備份」後提醒消失', not banner() and '已逾' not in pill(), pill())
    pg.click('#savepill button:text-is("儲存")')
    ok('按「儲存」的提示', toast() == '已儲存到這台電腦的瀏覽器', toast())
    ok('儲存後顯示時間', re.search(r'✓ 已自動儲存 \d\d:\d\d:\d\d', pill()), pill())
    hh = pg.evaluate("(() => { LAST_SAVED = new Date(2026, 10, 4, 0, 5, 9); updateBackupStatus(); return document.getElementById('savepill').textContent; })()")
    ok('午夜顯示 00:05:09', '已自動儲存 00:05:09' in hh, hh)
    bad = pg.evaluate("""(async () => { const o = Storage.prototype.setItem; Storage.prototype.setItem = () => { throw new Error('quota'); };
        await saveData(); Storage.prototype.setItem = o; const p = document.getElementById('savepill'); return [p.className, p.textContent]; })()""")
    ok('無法儲存時狀態列為紅色並提示', bad[0] == 'bad' and '儲存失敗：請勿關閉頁面，並盡快下載備份' in bad[1], bad)
    pg.evaluate('saveData()')
    ok('恢復後狀態列回到正常', pg.get_attribute('#savepill', 'class') == '')
    pg.emulate_media(media='print')
    ok('列印時隱藏狀態列與提醒', not pg.locator('#savepill').is_visible() and not banner())
    pg.emulate_media(media='screen')

    # 列印標題下方的學年度學期（規範第 14 節）
    term_at = """(iso) => { const R = Date, f = new R(iso + 'T10:00:00');
        window.Date = class extends R { constructor(...a) { if (a.length) super(...a); else super(f.getTime()); } static now() { return f.getTime(); } };
        try { return printTermLabel(); } finally { window.Date = R; } }"""
    pg.evaluate("DATA.settings.currentYear = ''; DATA.settings.currentSemester = ''")
    cases = {'2026-07-31': '114 學年度第 2 學期', '2026-08-01': '115 學年度第 1 學期',
             '2027-01-31': '115 學年度第 1 學期', '2027-02-01': '115 學年度第 2 學期'}
    got = {d: pg.evaluate(term_at, d) for d in cases}
    ok('未設定時依日期推算學年度學期（8/1、2/1 分界）', got == cases, got)
    pg.evaluate("DATA.settings.currentYear = '116'; DATA.settings.currentSemester = '2'")
    ok('有設定時用系統設定的學年度學期', pg.evaluate('printTermLabel()') == '116 學年度第 2 學期')
    with pg.expect_popup() as pop:
        pg.evaluate("_doDeidentExport('all')")
    w = pop.value; w.wait_for_load_state('load')
    ok('名冊列印有學年度學期', '116 學年度第 2 學期' in w.inner_text('.meta'), w.inner_text('.meta'))
    w.close()
    pg.evaluate("""DATA.schedules.push({ id: 'sch_t', title: '測試教師課表', periods: [{ period: '1', days: DAY_NAMES.map(() => '') }] }); scheduleSave()""")
    with pg.expect_popup() as pop:
        pg.evaluate("exportSchedulePDF('sch_t')")
    w = pop.value; w.wait_for_load_state('load')
    ok('課表列印有學年度學期', '116 學年度第 2 學期' in w.inner_text('body'))
    w.close()

    # 目前學期依日期自動、IEP 預設下一個要寫的學期（2026-11-04）
    at = lambda fn, iso: pg.evaluate("""([fn, iso]) => { const R = Date, f = new R(iso + 'T10:00:00');
        window.Date = class extends R { constructor(...a) { if (a.length) super(...a); else super(f.getTime()); } static now() { return f.getTime(); } };
        try { const t = window[fn](new Date()); return t.year + '/' + t.sem; } finally { window.Date = R; } }""", [fn, iso])
    iep = {'2026-09-01': '115/1', '2026-12-15': '115/2', '2027-01-20': '115/2', '2027-03-01': '115/2',
           '2027-05-10': '116/1', '2027-07-31': '116/1', '2027-08-01': '116/1'}
    got = {d: at('iepDefaultTerm', d) for d in iep}
    ok('IEP 預設學期（12～1 月→第二學期、5～7 月→下一學年度第一學期）', got == iep, got)
    pg.evaluate("DATA.settings.currentYear = ''; DATA.settings.currentSemester = ''; renderShell(); renderCurrentTab();")
    auto = pg.evaluate("(() => { const t = termByDate(new Date()); return t.year + '學年度第' + t.sem + '學期'; })()")
    ok('設定留白時副標依日期顯示學年度學期', pg.inner_text('.brand-school').endswith(auto), pg.inner_text('.brand-school'))
    pg.evaluate("setTab('settings')")
    pg.click('#content button:text-is("儲存設定")')
    ok('儲存設定後副標格式不變', pg.inner_text('.brand-school').endswith(auto), pg.inner_text('.brand-school'))
    mig = pg.evaluate("""(() => { const a = termByDate(new Date()); const keep = [DATA.settings.currentYear, DATA.settings.currentSemester];
        DATA.settings.currentYear = a.year; DATA.settings.currentSemester = a.sem; delete DATA.meta.termAuto; migrateData(); const r1 = [DATA.settings.currentYear, DATA.settings.currentSemester];
        DATA.settings.currentYear = '110'; DATA.settings.currentSemester = '2'; delete DATA.meta.termAuto; migrateData(); const r2 = [DATA.settings.currentYear, DATA.settings.currentSemester];
        DATA.settings.currentYear = keep[0]; DATA.settings.currentSemester = keep[1]; return [r1, r2]; })()""")
    ok('舊設定等於今天的學期→改為自動；不同→保留手動', mig == [['', ''], ['110', '2']], mig)
    pg.evaluate("DATA.settings.iepTemplate = 'data:x;base64,AA=='; setTab('students')")
    sid = pg.evaluate("DATA.students[0].id")
    pg.evaluate(f"openIEPExportModal('{sid}')")
    d = pg.evaluate("iepDefaultTerm()")
    ok('匯出 IEP 先選學年度學期，預設下一個要寫的學期', pg.input_value('#iep-year') == d['year'] and pg.input_value('#iep-sem') == d['sem'], (pg.input_value('#iep-year'), d))
    ph = pg.evaluate("(() => { const p = iepPlaceholders(DATA.students[0], {year: '116', sem: '2'}); return [p['{{學年度}}'], p['{{學期}}']]; })()")
    ok('IEP 佔位符用所選的學期', ph == ['116', '二'], ph)
    pg.evaluate("closeModal(); delete DATA.settings.iepTemplate")

    # 學生資料頁按鈕、課表節次名稱（2026-11-04）
    pg.evaluate("setTab('students')")
    btns = [x.strip() for x in pg.locator('#content .topbar-actions button').all_inner_texts()]
    ok('學生資料頁沒有「批次匯出 IEP」', '批次匯出 IEP' not in btns, btns)
    ok('按鈕「匯出學生名單」「去識別化列印」', '匯出學生名單' in btns and '去識別化列印' in btns and not any('SEIA' in b or 'PDF' in b for b in btns), btns)
    pg.evaluate("DATA.students.push({id: uid('s'), name: '測試二年級', class: '資二甲', seat: '2', studentId: 'T9', status: '在學', category: '學習障礙'}); migrateData();")
    pg.evaluate('openSeiaExport()')
    first = pg.locator('#modal-root .modal-foot button').first
    n1 = pg.evaluate("DATA.students.filter(s => !isArchived(s) && seiaStudent(s).grade === '一').length")
    ok('匯出名單預設（主要按鈕）為一年級在學學生', first.inner_text().startswith('一年級在學學生') and 'btn-primary' in first.get_attribute('class') and f'（{n1} 人）' in first.inner_text(), first.inner_text())
    with pg.expect_download() as dl3:
        first.click()
    names = [x['name'] for x in json.loads(pathlib.Path(dl3.value.path()).read_text(encoding='utf-8'))['students']]
    ok('一年級名單不含二年級學生', '測試二年級' not in names and len(names) == n1, names)
    labels = pg.evaluate("['1','2','10','11','一','第三節','早自習'].map(periodLabel)")
    ok('節次以國字顯示', labels == ['一', '二', '十', '十一', '一', '第三節', '早自習'], labels)
    pg.evaluate("setTab('schedule')")
    cells = pg.locator('#content .sched-period').all_inner_texts()
    ok('課表節次欄', cells[:2] == ['一', '二'], cells[:3])
    ok('「列印課表」按鈕', pg.locator('#content button:text-is("列印課表")').count() >= 1 and pg.locator('#content button:has-text("匯出 PDF")').count() == 0)

    # 列印視窗：不連網、會出現
    with pg.expect_popup() as pop:
        pg.evaluate("openPrintWindow('測試列印','<p>測試</p>')")
    w = pop.value; w.wait_for_load_state('load')
    ok('列印視窗有內容', '測試' in w.inner_text('body'))
    ok('列印視窗不載入外部樣式表', w.evaluate("document.querySelectorAll('link[rel=stylesheet]').length") == 0)
    w.close()

    # 夜間模式
    pg.emulate_media(color_scheme='dark'); pg.reload(); pg.wait_for_load_state('load')
    ok('夜間模式跟隨電腦設定', pg.evaluate("document.documentElement.getAttribute('data-theme')") == 'dark')

    ok('沒有對外請求', not external, external)
    ok('沒有 JS 錯誤', not errs, errs)
    b.close()

passed = sum(r[0] for r in results)
for good, name, detail in results:
    print(('PASS ' if good else 'FAIL ') + name + ('' if good or detail == '' else f'  ({detail})'))
print(f'\n{passed}/{len(results)} passed  ({HTML.name})')
sys.exit(0 if passed == len(results) else 1)
