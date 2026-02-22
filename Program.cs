using System;
using System.Windows.Forms;
using System.Net.Http;
using System.Text.Json;

namespace EzanApp {
    public class Program : Form {
        private Label lblKalan = new Label { Dock = DockStyle.Top, Height = 80, Font = new System.Drawing.Font("Segoe UI", 14, System.Drawing.FontStyle.Bold), TextAlign = System.Drawing.ContentAlignment.MiddleCenter, ForeColor = System.Drawing.Color.Red };
        private Label lblListe = new Label { Dock = DockStyle.Fill, Font = new System.Drawing.Font("Segoe UI", 11), Padding = new Padding(20) };
        private NotifyIcon notify = new NotifyIcon { Icon = System.Drawing.SystemIcons.Application, Visible = true };
        private System.Windows.Forms.Timer timer = new System.Windows.Forms.Timer { Interval = 1000 };
        private dynamic? vakitler;

        public Program() {
            this.Text = "Kağıthane Ezan Vakti";
            this.Size = new System.Drawing.Size(300, 400);
            this.Controls.Add(lblListe);
            this.Controls.Add(lblKalan);
            timer.Tick += (s, e) => Guncelle();
            _ = VeriCek();
            timer.Start();
        }

        async Task VeriCek() {
            try {
                var hc = new HttpClient();
                var res = await hc.GetStringAsync("https://api.aladhan.com/v1/timingsByCity?city=Istanbul&country=Turkey&method=13");
                var doc = JsonDocument.Parse(res);
                vakitler = doc.RootElement.GetProperty("data").GetProperty("timings");
                string txt = "BUGÜNKÜ VAKİTLER:\n\n";
                txt += $"İmsak: {vakitler.GetProperty("Fajr")}\nÖğle: {vakitler.GetProperty("Dhuhr")}\nİkindi: {vakitler.GetProperty("Asr")}\nAkşam: {vakitler.GetProperty("Maghrib")}\nYatsı: {vakitler.GetProperty("Isha")}";
                lblListe.Text = txt;
            } catch { lblKalan.Text = "İnternet Yok!"; }
        }

        void Guncelle() {
            if (vakitler == null) return;
            var simdi = DateTime.Now;
            string[] isimler = {"Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"};
            string[] tr = {"İmsak", "Öğle", "İkindi", "Akşam", "Yatsı"};
            
            for(int i=0; i<isimler.Length; i++) {
                var v = DateTime.Parse(vakitler.GetProperty(isimler[i]).GetString());
                var fark = v - simdi;
                if (fark.TotalSeconds > 0) {
                    lblKalan.Text = $"{tr[i]} Vaktine:\n{fark.Hours:D2}:{fark.Minutes:D2}:{fark.Seconds:D2}";
                    if (fark.TotalMinutes <= 10 && fark.TotalMinutes > 9.9) 
                        notify.ShowBalloonTip(5000, "Ezan Yaklaştı", $"{tr[i]} ezanına 10 dk kaldı.", ToolTipIcon.Info);
                    if (fark.TotalSeconds <= 1)
                        notify.ShowBalloonTip(5000, "Ezan Vakti", $"{tr[i]} ezanı okunuyor.", ToolTipIcon.Info);
                    break;
                }
            }
        }
        [STAThread] static void Main() => Application.Run(new Program());
    }
}
