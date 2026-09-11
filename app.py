<?php
require_once 'config.php';
check_auth();

$tab = $_GET['tab'] ?? 'simulasyon';
$sim_data = get_data('simulasyon.json');
$arsiv_data = get_data('arsiv.json');

// 1. Simülasyon Satırı Ekleme
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'add_sim') {
    $unite = $_POST['unite'];
    $il = $_POST['il'];
    $sure = (int)$_POST['sure'];
    $periyod = (float)$_POST['periyod'];
    $adet = (int)$_POST['adet'];

    $gunluk_gost = 1170;
    $baz_frekans = 1.0;
    $net_adet = 50;
    $endeks = 1.0;

    $frekans = round($baz_frekans * pow($adet / $net_adet, 0.55) * $endeks * pow($periyod, 0.80), 1);
    $toplam_gos = round($gunluk_gost * $sure * $adet);
    $erisim_kisi = $frekans > 0 ? round($toplam_gos / $frekans) : 0;
    $erisim_tr = round(($erisim_kisi / $TR_TOTAL_NUFUS) * 100, 2);
    $grp_tr = round(($toplam_gos / $TR_TOTAL_NUFUS) * 100, 2);

    $sim_data[] = [
        'unite' => $unite, 'il' => $il, 'sure' => $sure, 'periyod' => $periyod,
        'adet' => $adet, 'gosterim' => $toplam_gos, 'frekans' => $frekans,
        'erisim' => $erisim_kisi, 'il_nufus' => get_nufus($il),
        'tr_nufus' => $TR_TOTAL_NUFUS, 'erisim_tr' => $erisim_tr, 'grp_tr' => $grp_tr
    ];
    save_data('simulasyon.json', $sim_data);
    header('Location: dashboard.php?tab=simulasyon');
    exit;
}

// 2. Simülasyonu Marka Klasörüne / Arşive Kaydetme
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'save_to_archive') {
    $marka = $_POST['marka_adi'];
    $kampanya_adi = $_POST['kampanya_adi'];
    $yil = $_POST['yil'];
    $donem = $_POST['donem'];

    if (!empty($sim_data)) {
        foreach ($sim_data as $row) {
            $arsiv_data[] = [
                'yil' => $yil,
                'donem' => $donem,
                'marka' => $marka,
                'kampanya' => $kampanya_adi,
                'unite' => $row['unite'],
                'il' => $row['il'],
                'sure' => $row['sure'],
                'periyod' => $row['periyod'],
                'adet' => $row['adet'],
                'gosterim' => $row['gosterim'],
                'frekans' => $row['frekans'],
                'erisim' => $row['erisim'],
                'erisim_tr' => $row['erisim_tr'],
                'grp_tr' => $row['grp_tr']
            ];
        }
        save_data('arsiv.json', $arsiv_data);
        save_data('simulasyon.json', []); // Simülasyonu temizle
        header('Location: dashboard.php?tab=markalar&marka=' . urlencode($marka));
        exit;
    }
}

// Temizleme
if (isset($_GET['clear_sim'])) {
    save_data('simulasyon.json', []);
    header('Location: dashboard.php?tab=simulasyon');
    exit;
}

$master_brands = [
    "BİM", "Casper", "Hayat", "Kumtel", "Muratbey", "Namet", "Maret", "Kale",
    "File Market", "Kervan", "Kastamonu Entegre", "Biota", "Daikin", "Brita", "Doğanlar Holding",
    "Paribu", "Koton", "Geberit", "Yolcu360", "Weber", "Saint-Gobain", "Pasifik Holding",
    "Turna.com", "Herbalife", "Kopaş Kozmetik", "KFC", "Makarnam", "Pidem", "HD İskender",
    "Yataş", "Burgan Bank", "Milhans", "Çizmeci Time", "Hayat Finans", "Demant", "Siemens",
    "Pozitif", "Gloria Jean's", "Karnaval", "Bosch", "De'Longhi", "Braun", "Humm", "Evolvia"
];
?>
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>⚡ OOH Planlama & Simülasyon Merkezi</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: 'Outfit', sans-serif; }
        body { margin: 0; background: radial-gradient(circle at 50% -10%, #1a294d 0%, #0d1629 50%, #070b14 100%); color: #f8fafc; padding: 25px 40px; min-height: 100vh; }
        .app-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(56, 189, 248, 0.2); padding-bottom: 15px; margin-bottom: 25px; }
        .app-header h1 { font-size: 28px; font-weight: 800; background: linear-gradient(135deg, #38bdf8 0%, #60a5fa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
        .tabs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }
        .tab-btn { height: 50px; border-radius: 10px; font-weight: 700; font-size: 15px; text-decoration: none; display: flex; justify-content: center; align-items: center; transition: all 0.25s; border: 1.5px solid transparent; }
        .tab-btn.active { background: linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%); color: #fff; border-color: #38bdf8; box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45); }
        .tab-btn.inactive { background: linear-gradient(135deg, #111a2e 0%, #16223d 100%); color: #94a3b8; border-color: #233354; }
        .tab-btn.inactive:hover { color: #fff; border-color: #38bdf8; }
        
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin: 20px 0; }
        .kpi-card { background: linear-gradient(145deg, rgba(26, 38, 68, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1.5px solid rgba(56, 189, 248, 0.25); border-radius: 14px; padding: 18px 22px; }
        .kpi-title { font-size: 13px; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
        .kpi-val { font-size: 28px; font-weight: 800; color: #38bdf8; margin-top: 6px; }

        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; background-color: #0d1529; border: 1.5px solid rgba(56, 189, 248, 0.2); border-radius: 12px; overflow: hidden; }
        th { background: linear-gradient(180deg, #1a2747 0%, #141f38 100%); color: #38bdf8; padding: 14px; text-align: center; border-bottom: 2px solid #24355a; }
        td { padding: 12px; text-align: center; border-bottom: 1px solid #1a2747; color: #f1f5f9; }
        tr:hover { background-color: rgba(56, 189, 248, 0.06); }
        
        .input-row { display: grid; grid-template-columns: 2fr 2fr 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        select, input { height: 48px; border-radius: 10px; background-color: #131f3b; border: 1.5px solid #24355c; padding: 0 14px; font-size: 15px; color: #fff; width: 100%; outline: none; }
        select:focus, input:focus { border-color: #38bdf8; }
        .btn-green { height: 48px; width: 100%; border-radius: 10px; border: 1.5px solid #34d399; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #fff; font-weight: 700; font-size: 16px; cursor: pointer; }
        
        .folder-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px; }
        .folder-card { background: linear-gradient(145deg, #13203d 0%, #0c1426 100%); border: 1.5px solid rgba(56, 189, 248, 0.25); border-radius: 14px; padding: 20px; text-align: center; text-decoration: none; color: #38bdf8; font-weight: 700; font-size: 16px; display: block; transition: all 0.25s; box-shadow: 0 8px 20px rgba(0,0,0,0.35); }
        .folder-card:hover { transform: translateY(-3px); border-color: #38bdf8; background: linear-gradient(145deg, #1c2e56 0%, #101c36 100%); color: #fff; }
        .save-box { background: #131f3b; border: 1.5px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 20px; margin-top: 25px; }
    </style>
</head>
<body>
    <div class="app-header">
        <h1>⚡ OOH PLANLAMA & SİMÜLASYON MERKEZİ</h1>
        <div><a href="index.php" style="color: #f87171; text-decoration: none; font-weight: 600;">🚪 Çıkış Yap</a></div>
    </div>

    <div class="tabs">
        <a href="dashboard.php?tab=simulasyon" class="tab-btn <?= $tab === 'simulasyon' ? 'active' : 'inactive' ?>">📊 Anlık Hesaplama & Simülatör</a>
        <a href="dashboard.php?tab=arsiv" class="tab-btn <?= $tab === 'arsiv' ? 'active' : 'inactive' ?>">📁 Kampanya Yönetimi & Arşiv</a>
        <a href="dashboard.php?tab=markalar" class="tab-btn <?= $tab === 'markalar' ? 'active' : 'inactive' ?>">🏢 Markalarımız & Portföy</a>
    </div>

    <!-- 1. SEKME: SİMÜLASYON -->
    <?php if ($tab === 'simulasyon'): ?>
        <form method="POST">
            <input type="hidden" name="action" value="add_sim">
            <div class="input-row">
                <select name="il">
                    <option value="Anadolu İlleri">Anadolu İlleri</option>
                    <option value="İstanbul">İstanbul</option>
                    <option value="Ankara">Ankara</option>
                    <option value="İzmir">İzmir</option>
                </select>
                <select name="unite">
                    <option value="Afiş Değiştiricili Megalight">Afiş Değiştiricili Megalight</option>
                    <option value="Billboard">Billboard</option>
                    <option value="Durak Raket CLP">Durak Raket CLP</option>
                    <option value="Dijital Ekran">Dijital Ekran</option>
                </select>
                <input type="number" step="0.1" name="periyod" value="1.0" placeholder="Periyod">
                <input type="number" name="sure" value="7" placeholder="Süre (Gün)">
                <input type="number" name="adet" value="50" placeholder="Adet">
            </div>
            <button type="submit" class="btn-green">➕ Simülasyon Satırını Plana Ekle</button>
        </form>

        <?php if (!empty($sim_data)): 
            $tot_gos = array_sum(array_column($sim_data, 'gosterim'));
            $tot_grp = array_sum(array_column($sim_data, 'grp_tr'));
        ?>
            <div class="kpi-grid">
                <div class="kpi-card"><div class="kpi-title">Toplam Gösterim</div><div class="kpi-val"><?= tr_tam_sayi($tot_gos) ?></div></div>
                <div class="kpi-card"><div class="kpi-title">Toplam TR GRP</div><div class="kpi-val"><?= tr_ondalik($tot_grp, 2) ?></div></div>
                <div class="kpi-card"><div class="kpi-title">Maks. TR Erişimi</div><div class="kpi-val">%18,1</div></div>
                <div class="kpi-card"><div class="kpi-title">Kapsanan İl</div><div class="kpi-val">1 İl</div></div>
            </div>

            <table>
                <thead>
                    <tr><th>Ünite</th><th>İl</th><th>Süre</th><th>Periyod</th><th>Adet</th><th>Toplam Gösterim</th><th>Frekans</th><th>TR Erişim %</th><th>TR GRP</th></tr>
                </thead>
                <tbody>
                    <?php foreach ($sim_data as $row): ?>
                        <tr>
                            <td><?= $row['unite'] ?></td><td><?= $row['il'] ?></td><td><?= $row['sure'] ?></td>
                            <td><?= $row['periyod'] ?></td><td><?= tr_tam_sayi($row['adet']) ?></td>
                            <td><?= tr_tam_sayi($row['gosterim']) ?></td><td><?= tr_ondalik($row['frekans'], 1) ?></td>
                            <td>%<?= tr_ondalik($row['erisim_tr'], 2) ?></td><td><?= tr_ondalik($row['grp_tr'], 2) ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>

            <div style="display: flex; gap: 15px; align-items: center; justify-content: space-between;">
                <a href="dashboard.php?clear_sim=1" style="background: #ef4444; color: #fff; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 700;">🧹 Tümünü Temizle</a>
                <a href="export.php?type=excel&source=sim" style="background: #0ea5e9; color: #fff; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 700;">📊 Excel Raporu İndir</a>
            </div>

            <!-- ARŞİVE VE MARKA KLASÖRÜNE KAYDET FORMBOX -->
            <div class="save-box">
                <h3 style="color: #38bdf8; margin-top: 0; font-size: 18px;">📁 Bu Planı Marka Klasörüne / Arşive Kaydet</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="save_to_archive">
                    <div style="display: grid; grid-template-columns: 2fr 2fr 1fr 1fr 2fr; gap: 12px; align-items: center;">
                        <select name="marka_adi" required>
                            <option value="">Marka Seçiniz...</option>
                            <?php foreach ($master_brands as $mb): ?>
                                <option value="<?= $mb ?>"><?= $mb ?></option>
                            <?php endforeach; ?>
                        </select>
                        <input type="text" name="kampanya_adi" placeholder="Kampanya Adı (Örn: Lansman)" required>
                        <input type="number" name="yil" value="2026" required>
                        <select name="donem">
                            <option value="Ocak">Ocak</option><option value="Şubat">Şubat</option><option value="Mart">Mart</option>
                            <option value="Nisan">Nisan</option><option value="Mayıs">Mayıs</option><option value="Haziran">Haziran</option>
                            <option value="Temmuz">Temmuz</option><option value="Ağustos">Ağustos</option><option value="Eylül">Eylül</option>
                            <option value="Ekim">Ekim</option><option value="Kasım">Kasım</option><option value="Aralık">Aralık</option>
                        </select>
                        <button type="submit" style="background: #10b981; color: #fff; border: none; border-radius: 10px; font-weight: 700; height: 48px; cursor: pointer;">💾 Klasöre Kaydet</button>
                    </div>
                </form>
            </div>
        <?php endif; ?>

    <!-- 2. SEKME: ARŞİV -->
    <?php elseif ($tab === 'arsiv'): ?>
        <h3 style="color: #38bdf8;">📁 Tüm Arşivlenen Kampanyalar</h3>
        <?php if (empty($arsiv_data)): ?>
            <p style="color: #94a3b8;">Henüz arşive kaydedilmiş kampanya bulunmuyor.</p>
        <?php else: ?>
            <table>
                <thead>
                    <tr><th>Yıl</th><th>Dönem</th><th>Marka</th><th>Kampanya</th><th>Ünite</th><th>İl</th><th>Adet</th><th>Toplam Gösterim</th><th>TR GRP</th></tr>
                </thead>
                <tbody>
                    <?php foreach ($arsiv_data as $ar): ?>
                        <tr>
                            <td><?= $ar['yil'] ?></td><td><?= $ar['donem'] ?></td><td><strong><?= $ar['marka'] ?></strong></td>
                            <td><?= $ar['kampanya'] ?></td><td><?= $ar['unite'] ?></td><td><?= $ar['il'] ?></td>
                            <td><?= tr_tam_sayi($ar['adet']) ?></td><td><?= tr_tam_sayi($ar['gosterim']) ?></td><td><?= tr_ondalik($ar['grp_tr'], 2) ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>

    <!-- 3. SEKME: MARKALARIMIZ & KLASÖRLER -->
    <?php elseif ($tab === 'markalar'): ?>
        <?php 
        $secilen_marka = $_GET['marka'] ?? '';
        if ($secilen_marka === ''): 
        ?>
            <h3 style="color: #38bdf8;">🏢 Müşteri Portföyü & Kampanya Klasörleri</h3>
            <p style="color: #94a3b8;">Geçmiş kampanyalarını incelemek istediğiniz markanın klasörüne tıklayın:</p>
            <div class="folder-grid">
                <?php foreach ($master_brands as $mb): 
                    $m_count = 0;
                    foreach ($arsiv_data as $ad) { if ($ad['marka'] === $mb) $m_count++; }
                ?>
                    <a href="dashboard.php?tab=markalar&marka=<?= urlencode($mb) ?>" class="folder-card">
                        📁 <?= $mb ?><br>
                        <span style="font-size: 12.5px; color: #94a3b8; font-weight: 500;">(<?= $m_count ?> Kampanya)</span>
                    </a>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                <a href="dashboard.php?tab=markalar" style="background: #1e293b; color: #38bdf8; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: 700;">⬅️ Tüm Markalara Dön</a>
                <h2 style="color: #38bdf8; margin: 0;">📁 <?= htmlspecialchars($secilen_marka) ?> Kampanya Geçmişi</h2>
            </div>
            
            <?php 
            $marka_rows = array_filter($arsiv_data, function($v) use ($secilen_marka) { return $v['marka'] === $secilen_marka; });
            if (empty($marka_rows)): 
            ?>
                <p style="color: #f87171;">Bu markaya ait henüz arşivlenmiş bir kampanya kaydı bulunmuyor. Anlık simülasyondan plan oluşturup bu klasöre kaydedebilirsiniz.</p>
            <?php else: 
                $m_gos = array_sum(array_column($marka_rows, 'gosterim'));
                $m_grp = array_sum(array_column($marka_rows, 'grp_tr'));
            ?>
                <div class="kpi-grid">
                    <div class="kpi-card"><div class="kpi-title">Toplam Gösterim</div><div class="kpi-val"><?= tr_tam_sayi($m_gos) ?></div></div>
                    <div class="kpi-card"><div class="kpi-title">Toplam TR GRP</div><div class="kpi-val"><?= tr_ondalik($m_grp, 2) ?></div></div>
                    <div class="kpi-card"><div class="kpi-title">Kampanya Sayısı</div><div class="kpi-val"><?= count($marka_rows) ?></div></div>
                </div>

                <table>
                    <thead>
                        <tr><th>Yıl</th><th>Dönem</th><th>Kampanya Adı</th><th>Mecra</th><th>Ünite</th><th>İl</th><th>Adet</th><th>Toplam Gösterim</th><th>TR GRP</th></tr>
                    </thead>
                    <tbody>
                        <?php foreach ($marka_rows as $mr): ?>
                            <tr>
                                <td><?= $mr['yil'] ?></td><td><?= $mr['donem'] ?></td><td><strong><?= $mr['kampanya'] ?></strong></td>
                                <td>Kentvizyon</td><td><?= $mr['unite'] ?></td><td><?= $mr['il'] ?></td>
                                <td><?= tr_tam_sayi($mr['adet']) ?></td><td><?= tr_tam_sayi($mr['gosterim']) ?></td><td><?= tr_ondalik($mr['grp_tr'], 2) ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
        <?php endif; ?>
    <?php endif; ?>
</body>
</html>
