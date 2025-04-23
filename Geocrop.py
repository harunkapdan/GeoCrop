import pandas as pd
import geopandas as gpd
import os
import re
import logging
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'islem.log'),
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Tarım Parsel Verilerinin Coğrafi ve Sayısal Olarak İşlenmesi
# Bu kod, tarımsal parsel verilerini (GML) ve üretim verilerini (Excel) birleştirerek
# gpkg, excel ve geojson çıktılarını üretir.

def parsel_kodu_olustur(x):
	return f"{x[0]}_{x[1]}_{x[2]}/{x[3]}"

def geometri_gecerli(gdf):
	return gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon']).all()

def log_cikti(dosya_yolu, tur):
	logging.info(f"Bitki {tur} oluşturuldu: {dosya_yolu}")

def main():
    try:
	    # Girdi dosyaları ve klasörleri
        excel_path = r"C:\\Users\\hrnkp\\OneDrive\\Masaüstü\\excels\\CKS_KoyGenelindeParselUretim.xlsx"
        gml_klasor = r"C:\\Users\\hrnkp\\OneDrive\\Masaüstü\\TP_MERKEZ_11_02_2025"
        cikti_klasor = "cikti_dosyalar"
        bitki_gpkg_dir = os.path.join(cikti_klasor, "gpkg")
        bitki_excel_dir = os.path.join(cikti_klasor, "excel")
        bitki_geojson_dir = os.path.join(cikti_klasor, "geojson")

        for klasor in [bitki_gpkg_dir, bitki_excel_dir, bitki_geojson_dir]:
            os.makedirs(klasor, exist_ok=True)

        if not os.path.exists(excel_path):
            logging.error("Excel dosyası bulunamadı!")
            raise FileNotFoundError("Excel dosyası bulunamadı!")

        if not os.path.exists(gml_klasor):
            logging.error("GML klasörü bulunamadı!")
            raise FileNotFoundError("GML klasörü bulunamadı!")

        logging.info("Girdi dosyaları ve klasörler kontrol edildi.")

        logging.info("Excel verisi işleniyor...")
        df = pd.read_excel(excel_path, header=10)
        df.columns = df.columns.str.strip().str.replace("\n", " ")

        rename_map = {
            "İlçe": "Ilce",
            "Köy": "Koy",
            "Ada No": "Ada_No",
            "Parsel No": "Parsel_No",
            "Parsel  Alanı(da)": "Parsel_alani",
            "Ekili  Alan (da)": "Ekili_Alan",
            "Ürün": "Urun"
        }
        df.rename(columns=rename_map, inplace=True)

        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df["Ekili_Alan"] = pd.to_numeric(df["Ekili_Alan"], errors="coerce")
        df["Parsel_alani"] = pd.to_numeric(df["Parsel_alani"], errors="coerce")
        # Ürün adlarındaki parantez içi bilgileri temizle
        df["Urun"] = df["Urun"].astype(str).apply(lambda x: re.sub(r"\(.*?\)", "", x).strip())

        # Bitki gruplandırma
        bitki_map = {
            "buğday": "Hububat",
            "arpa": "Hububat",
            "aspir": "Aspir",
            "nadas": "Diğer"
        }

        # Bitki gruplama işlemi
        df["Bitki"] = df["Urun"].str.lower()
        df["Bitki_Grubu"] = df["Bitki"].apply(lambda x: bitki_map.get(x, "diğer"))

        # Parsel Kodu oluşturma
        df["Anahtar"] = df[["Ilce", "Koy", "Ada_No", "Parsel_No"]].astype(str).agg("/".join, axis=1)
        df["Tarımsal_No"] = range(1, len(df) + 1)
        df["Parsel_Kodu"] = df[["Ilce", "Koy", "Ada_No", "Parsel_No"]].astype(str).agg(parsel_kodu_olustur, axis=1)

        df["Yer"] = df[["Ilce", "Koy"]].astype(str).agg("/".join, axis=1)
        df["Etopla"] = df.groupby("Bitki")["Ekili_Alan"].transform("sum")
        df["Çok_Etopla"] = df.groupby("Bitki_Grubu")["Ekili_Alan"].transform("sum")
        df.dropna(axis=1, how="all", inplace=True)
        logging.info("Excel verisi başarıyla işlendi.")

        logging.info("GML dosyaları okunuyor...")
        gml_list = []

        for dosya in os.listdir(gml_klasor):
            if dosya.endswith(".gml"):
                yol = os.path.join(gml_klasor, dosya)
                try:
						# GML dosyasını oku
                    gdf = gpd.read_file(yol)[["IlceAd", "MahalleAd", "AdaNo", "ParselNo", "geometry"]]
                    # Gereksiz sütunları kaldır
                    gdf = gdf[["IlceAd", "MahalleAd", "AdaNo", "ParselNo", "geometry"]]
                    gdf.columns = ["Ilce", "Koy", "Ada_No", "Parsel_No", "geometry"]
                    gdf["Parsel_Kodu"] = gdf[["Ilce", "Koy", "Ada_No", "Parsel_No"]].astype(str).agg(parsel_kodu_olustur, axis=1)
                    gml_list.append(gdf)
                    logging.info(f"GML dosyası okundu: {dosya}")
                except Exception as e:
                    logging.warning(f"GML dosyası okunamadı: {dosya} → {e}")

        if not gml_list:
            logging.error("Hiçbir GML dosyası okunamadı!")
            raise ValueError("Hiçbir GML dosyası okunamadı!")
				 # Tüm GML'leri birleştir
        full_gdf = pd.concat(gml_list)

        logging.info("Excel ve GML verileri eşleştiriliyor...")
        merged = full_gdf.merge(df, on="Parsel_Kodu", how="left").dropna(subset=["Bitki"])

					# Her bitki türü için ayrı çıktı üretiliyor
        for bitki in merged["Bitki"].dropna().unique():
            bitki_gdf = merged[merged["Bitki"] == bitki].copy()
            if not bitki_gdf.empty:
                dosya_adi = "".join(c if c.isalnum() else "_" for c in bitki)

                #gpkg kaydetme
                gpkg_path = os.path.join(bitki_gpkg_dir, f"{dosya_adi}.gpkg")
                bitki_gdf.to_file(gpkg_path, driver="GPKG")
                log_cikti(gpkg_path, "GeoPackage")

                #excel kaydetme
                excel_path = os.path.join(bitki_excel_dir, f"{dosya_adi}.xlsx")
                bitki_gdf.drop(columns="geometry").to_excel(excel_path, index=False)
                log_cikti(excel_path, "Excel")

                #geojson kaydetme
                if geometri_gecerli(bitki_gdf):
                    try:
                        geojson_path = os.path.join(bitki_geojson_dir, f"{dosya_adi}.geojson")
                        bitki_gdf.to_file(geojson_path, driver="GeoJSON")
                        log_cikti(geojson_path, "GeoJSON")
                    except Exception as e:
                        logging.warning(f"GeoJSON üretilemedi ({dosya_adi}): {e}")
                else:
                    logging.warning(f"GeoJSON üretilemedi (geçersiz geometri): {dosya_adi}")

        logging.info("Tüm işlemler başarıyla tamamlandı. Çıktılar klasörlere kaydedildi.")
        print("Tüm işlemler başarıyla tamamlandı.")
        print(f"  - GeoPackage dosyaları: {bitki_gpkg_dir}")
        print(f"  - GeoJSON dosyaları: {bitki_geojson_dir}")
        print(f"  - Excel dosyaları: {bitki_excel_dir}")
        return 0

    except Exception as e:
        logging.error(f"Program hatası: {e}")
        print(f"Hata: {e}")
        return 1
if __name__ == "__main__":
    main()
