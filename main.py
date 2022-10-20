import tkinter
import requests

WINDOW_HEIGHT = 700
WINDOW_WIDTH = 1000
BASE_API_URL = "https://api.hh.ru"

# Класс приложения
class HeadHunterAPIApplication(tkinter.Frame):
    # Создание экземпляра приложения
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
        self._center_window()
    # Создание интерфейса приложения: кнопки, текстовые поля, надписи
    def _init_ui(self):
        # Установка заголовка окна и размещение основной области на экране
        self.master.title("Поиск вакансий на HH.ru")
        self.pack(fill=tkinter.BOTH, expand=True)

        # Создание надписи и размещение ее на экране
        self.label_region = tkinter.Label(self, text="Укажите регион (страна, область, город):",
                                          bg="white", fg="black", font=14, justify="center")
        self.label_region.pack()

        # Создание поля для ввода текста, установка ему значения по умолчанию и размещение его на экране
        self.entry_region = tkinter.Entry(self, bg="white", fg="black", font=14, justify="left", borderwidth=3)
        self.entry_region.insert(0, "Россия")
        self.entry_region.pack()

        # Создание надписи и размещение ее на экране
        self.label_vacancy = tkinter.Label(self, text="Укажите профессию или должность:",
                                           bg="white", fg="black", font=14, justify="center")
        self.label_vacancy.pack()

        # Создание поля для ввода текста, установка ему значения по умолчанию и размещение его на экране
        self.entry_vacancy = tkinter.Entry(self, bg="white", fg="black", font=14, justify="left", borderwidth=3)
        self.entry_vacancy.insert(0, "python программист")
        self.entry_vacancy.pack()

        # Создание кнопки и размещение ее на экране
        self.btn_search = tkinter.Button(self, text="Найти", command=self._get_data,
                                         relief="raised", font=20, borderwidth=8, width=14, )
        self.btn_search.pack()

        # Создание общего контейнера для текстового поля и полосы прокрутки и размещение его на экране
        self.frame_output = tkinter.Frame(self)
        self.frame_output.pack(fill="both")

        # Создание большого текстового поля, в котором будут отображаться результаты поиска, и размещение его на экране
        self.txt_result = tkinter.Text(self.frame_output, bg="white", fg="black", font=14,
                                       wrap="word", relief="sunken", borderwidth=3, width=108)
        self.txt_result.pack(side="left")

        # Создание полосы прокрутки для текстового поля и размещение ее на экране
        self.txt_scroller = tkinter.Scrollbar(self.frame_output, command=self.txt_result.yview)
        self.txt_scroller.pack(side="left", fill="y")

    # Функция устанавливает окно приложения по центру экрана
    def _center_window(self):
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        window_x = (screen_width - WINDOW_WIDTH) / 2
        window_y = (screen_height - WINDOW_HEIGHT) / 2

        self.parent.geometry('%dx%d+%d+%d' % (WINDOW_WIDTH, WINDOW_HEIGHT, window_x, window_y))

    # Функция обращения к API hh.ru
    def _get_data(self):
        # Очистка текстового поля
        self.txt_result.delete(1.0, tkinter.END)

        # Получение введенного пользователем значения професии
        vacancy = self.entry_vacancy.get().replace(" ", "+")

        # Получение id введенного пользователем региона
        region_id = self._get_region_id()
        if region_id == -1:
            self.txt_result.insert(1.0, "Указанный регион не найден, убедитесь в правильности написания")
            return

        # Обращение к API и получение списка подходящих вакансий
        vacancies_list = requests.get(f"{BASE_API_URL}/vacancies?area={region_id}&text={vacancy}&page=1&per_page=10")

        # Проверка кода ответа, возвращенного сервером
        if vacancies_list.status_code == 200:
            # Преобразование полученного списка в json формат, получение из него некоторых данных
            # и их вывод в текстовое поле
            vacancies_list = vacancies_list.json()["items"]
            for vac in vacancies_list:
                self.txt_result.insert(tkinter.END,
                            f"Должность: {vac['name']};\n\tРегион: {vac['area']['name']};\n"
                            f"\tКомпания: {vac['employer']['name']};\n"
                            f"\tЗарплата: от {vac['salary']['from'] if vac['salary'] else 'з/п не указана'};\n"
                            f"\tТребования: {vac['snippet']['requirement']};\n"
                            f"\tОбязанности: {vac['snippet']['responsibility']}\n\n\n")

        # При получении любого кода ошибки - вывод его номера и уведомления об этом
        else:
            self.txt_result.insert(1.0, f"Ошибка {vacancies_list.status_code}\n"
                                        f"Не удалось найти указанную профессию")
            return

    # функция получения id необходимого региона, для последующего его использования в запросе в качестве параметра
    def _get_region_id(self) -> int:
        # Получение введенного пользователем региона
        region_name = self.entry_region.get()
        # Приведение названия региона к формату, необходимому для передачи в качестве параметра в url
        url_region_name = self.entry_region.get().replace(" ", "+")

        # Запрос к API и получение списка подходящих регионов
        list_of_similar_regions = requests.get(f"{BASE_API_URL}/suggests/areas?text={url_region_name}")

        # Проверка кода ответа, возвращенного сервером
        if list_of_similar_regions.status_code == 200:
            # Преобразование полученного списка в json формат
            # Если не существует ни одного похожего на указанный пользователем регион(т.е. список пуст),
            # то будет возвращена ошибка
            if not (list_of_similar_regions := list_of_similar_regions.json()["items"]):
                return -1

            region_id = -1
            # Поиск полного совпадения указанного региона с регионом из списка и получение его id
            for reg in list_of_similar_regions:
                if reg["text"] == region_name:
                    region_id = reg["id"]
                    break

            # Если точное совпадение не найдено, то берется первый вариант из списка
            if region_id == -1:
                region_id = list_of_similar_regions[0]["id"]

            # Возвращается полученный id региона
            return region_id

        # При получении любого кода ошибки - вывод его номера и уведомления об этом
        else:
            self.txt_result.insert(1.0, f"Ошибка {list_of_similar_regions.status_code}")
            return -1


if __name__ == '__main__':
    # Создание экземпляра приложения
    root = tkinter.Tk()
    app = HeadHunterAPIApplication(root)
    # Запуск приложения()
    root.mainloop()
