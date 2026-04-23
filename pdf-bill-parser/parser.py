import pdfplumber
import pandas as pd
import os
import sys
from pathlib import Path

# ------------------ PATHS ------------------

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS).parent
    return Path().resolve()

base_dir = get_base_dir()
pdf_folder = base_dir / "data" / "2026-03"

# ------------------ CONFIG ------------------

SERVICE_MAPPING = {
    "ПУ №10388468": "Электроэнергия",
    "Холодное водоснабжение (4.32)": "ХВС",
    "Стоки ХВ (4.32)": "ХВС - Водоотведение",
    "Вода для ГВС (3.15)": "Вода для ГВС",
    "Стоки ГВ (3.15)": "ГВС - Водоотведение",
    "Нагрев ГВ": "Нагрев ГВ",
    "Отопление": "Отопление",
    "Нагрев ГВ СОИД": "Нагрев ГВ / общедом",
    "ГВ снаб СОИД": "ГВС / общедом",
    "Теплонос.СОИД": "ГВС / общедом",
    "ХВ снабж. СОИД": "ХВС / общедом",
    "Отв.ст.вод СОИД": "Водоотведение / общедом",
    "Эл.снабж. СОИД": "Электроэнергия / общедом",
    "Тех.обслуживание": "Тех.обслуживание дома",
    "Сод.общ.имущ.": "Содержание общего имущества",
    "ТКО": "Вывоз мусора",
    "Взнос на капитальный ремонт": "Капремонт",
}

SERVICE_ORDER = [
    "Электроэнергия",
    "ХВС",
    "ХВС - Водоотведение",
    "Вода для ГВС",
    "ГВС - Водоотведение",
    "Нагрев ГВ",
    "Отопление",
    "Нагрев ГВ / общедом",
    "ГВС / общедом",
    "ХВС / общедом",
    "Водоотведение / общедом",
    "Электроэнергия / общедом",
    "Тех.обслуживание дома",
    "Содержание общего имущества",
    "Вывоз мусора",
    "Капремонт",
]

# ------------------ HELPERS ------------------

def map_service(name):
    for key, value in SERVICE_MAPPING.items():
        if key in name:
            return value
    return name


def format_number_for_excel(num_str):
    if not num_str:
        return ""
    num_str = num_str.replace(" ", "").replace(",", ".")
    try:
        return f"{float(num_str)}".replace(".", ",")
    except:
        return num_str


# ------------------ PARSERS (UNCHANGED) ------------------

def parse_jeu5(pdf, period):
    data = []
    seen_services = set()

    for page in pdf.pages:
        table = page.extract_table()
        if not table:
            continue

        for row in table:
            if not row or row[0] in [
                None,
                'Предельный (максимальный) индекс изменения размера платы граждан за коммунальные услуги в муниципальном образовании, %',
                'Коммунальные услуги',
                'Дополнительные услуги',
                'Виды услуг',
                '1',
                'Итого к оплате за расчетный период'
            ]:
                continue

            raw_service = row[0].strip()
            service = SERVICE_MAPPING.get(raw_service, raw_service)

            if service in seen_services:
                continue
            seen_services.add(service)

            try:
                volume_raw = row[2] if row[2] and row[2].strip() != "-" else row[3]
                volume = format_number_for_excel(volume_raw.split()[0].replace(",", "."))
                tariff = format_number_for_excel(row[4].replace(" ", "").replace(",", ".")) if row[4] else ""
                total = format_number_for_excel(row[10].replace(" ", "").replace(",", ".")) if row[10] else ""

                data.append({
                    "период": period,
                    "услуга": service,
                    "объем_квит": volume,
                    "тариф_квит": tariff,
                    "начислено_квит": total
                })

            except Exception as e:
                print("⚠️ ЖЭУ5:", row, "|", e)

    return data


def parse_cap_remont(pdf, period):
    data = []

    for page in pdf.pages:
        table = page.extract_table()
        if not table:
            continue

        for row in table:
            if row and row[0] == 'Взнос на капитальный ремонт':
                try:
                    raw_service = row[0].strip()
                    service = SERVICE_MAPPING.get(raw_service, raw_service)

                    volume = format_number_for_excel(row[2].replace(",", ".")) if row[2] else ""
                    tariff = format_number_for_excel(row[4].replace(" ", "").replace(",", ".")) if row[4] else ""
                    total = format_number_for_excel(row[5].replace(" ", "").replace(",", ".")) if row[5] else ""

                    data.append({
                        "период": period,
                        "услуга": service,
                        "объем_квит": volume,
                        "тариф_квит": tariff,
                        "начислено_квит": total
                    })

                except Exception as e:
                    print("⚠️ КапРемонт:", row, "|", e)

    return data


def parse_tko(pdf, period):
    data = []

    for page in pdf.pages:
        table = page.extract_table()
        if not table:
            continue

        for row in table:
            if row and row[0] not in [
                'Услуга',
                'Всего к оплате, с учетом начислений, перерасчета, оплаты и пени руб.:'
            ]:
                try:
                    raw_service_name = ' '.join(part.strip() for part in row if isinstance(part, str))
                    service = map_service(raw_service_name)

                    tariff = format_number_for_excel(row[2].replace(" ", "").replace(",", ".")) if row[2] else ""
                    volume = format_number_for_excel(row[3].replace(",", ".")) if row[3] else ""
                    total = format_number_for_excel(row[4].replace(" ", "").replace(",", ".")) if row[4] else ""

                    data.append({
                        "период": period,
                        "услуга": service,
                        "объем_квит": volume,
                        "тариф_квит": tariff,
                        "начислено_квит": total
                    })

                except Exception as e:
                    print("⚠️ ТКО:", row, "|", e)

    return data


def parse_water(pdf, period):
    data = []

    for page in pdf.pages:
        table = page.extract_table()
        if not table:
            continue

        for row in table:
            if row and row[0] in [
                'Холодное водоснабжение (4.32)',
                'Стоки ХВ (4.32)',
                'Стоки ГВ (3.15)',
                'Вода для ГВС (3.15)'
            ]:
                try:
                    raw_service = row[0].strip()
                    service = SERVICE_MAPPING.get(raw_service, raw_service)

                    volume = format_number_for_excel(row[3].replace(",", ".")) if row[3] else ""
                    tariff = format_number_for_excel(row[5].replace(" ", "").replace(",", ".")) if row[5] else ""
                    total = format_number_for_excel(row[6].replace(" ", "").replace(",", ".")) if row[6] else ""

                    data.append({
                        "период": period,
                        "услуга": service,
                        "объем_квит": volume,
                        "тариф_квит": tariff,
                        "начислено_квит": total
                    })

                except Exception as e:
                    print("⚠️ Вода:", row, "|", e)

    return data


def parse_electricity(pdf, period):
    data = []

    for page in pdf.pages:
        table = page.extract_table()
        if not table:
            continue

        for row in table:
            if row and row[0] == 'ПУ №10388468':
                try:
                    raw_service = row[0].strip()
                    service = SERVICE_MAPPING.get(raw_service, raw_service)

                    volume = format_number_for_excel(row[6].replace(",", ".")) if row[6] else ""
                    tariff = format_number_for_excel(row[9].replace(" ", "").replace(",", ".")) if row[9] else ""
                    total = format_number_for_excel(row[10].replace(" ", "").replace(",", ".")) if row[10] else ""

                    data.append({
                        "период": period,
                        "услуга": service,
                        "объем_квит": volume,
                        "тариф_квит": tariff,
                        "начислено_квит": total
                    })

                except Exception as e:
                    print("⚠️ Электро:", row, "|", e)

    return data


# ------------------ DETECTION ------------------

def detect_and_parse(pdf_path):
    period = f"{pdf_path.parent.name}-01"

    with pdfplumber.open(pdf_path) as pdf:
        first_page_text = pdf.pages[0].extract_text() or ""

        print(f"📄 Файл: {pdf_path.name}")

        if 'ЖЭУ-5' in first_page_text:
            return parse_jeu5(pdf, period)
        elif 'капитальный ремонт' in first_page_text.lower():
            return parse_cap_remont(pdf, period)
        elif 'ТКО' in first_page_text or 'вывоз' in first_page_text.lower():
            return parse_tko(pdf, period)
        elif 'водоснабжение' in first_page_text:
            return parse_water(pdf, period)
        elif 'ПУ №10388468' in first_page_text:
            return parse_electricity(pdf, period)
        else:
            print(f"❓ Неизвестный формат: {pdf_path.name}")
            return []


# ------------------ MAIN ------------------

def main():
    if not pdf_folder.exists():
        print(f"❌ Папка не найдена: {pdf_folder}")
        return

    all_data = []

    for pdf_file in pdf_folder.glob("*.pdf"):
        parsed = detect_and_parse(pdf_file)
        all_data.extend(parsed)

    if not all_data:
        print("⚠️ Нет данных для сохранения.")
        return

    df = pd.DataFrame(all_data)

    df["услуга"] = pd.Categorical(
        df["услуга"],
        categories=SERVICE_ORDER,
        ordered=True
    )

    df = df.sort_values(["период", "услуга"]).reset_index(drop=True)

    excel_path = base_dir / "output_data.xlsx"
    csv_path = base_dir / "output_data.csv"

    if excel_path.exists():
        excel_path.unlink()

    if csv_path.exists():
        csv_path.unlink()

    df.to_excel(excel_path, index=False)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print(f"✅ Сохранено: {excel_path}")
    print(f"✅ Сохранено: {csv_path}")

    os.startfile(excel_path)


if __name__ == "__main__":
    main()