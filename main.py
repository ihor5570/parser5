from comparison.start import start_scraping
from utils import delete_temp_files
from xlsx import collect_excel_file, create_input_data


def main():
    delete_temp_files()
    create_input_data()
    start_scraping()
    collect_excel_file()

if __name__ == "__main__":
    main()
