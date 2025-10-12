import requests, datetime, os, urllib3, string

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
outputDirectory = "output"
allowedChars = string.ascii_letters + string.digits + "-"

def requestApiData(session: requests.Session, url : str):
    """
    Выполняет HTTP-запрос к указанному API и возвращает ответ в формате JSON.

    Args:
        session (requests.Session): Сессия Requests с предварительно заданными параметрами.
        url (str): Полный URL для запроса.

    Returns:
        dict | list: Распознанный JSON-ответ сервера.

    Raises:
        SystemExit: В случае ошибок сети, соединения или некорректного ответа.
    """
    try:
        apiResponse : requests.Response = session.get(url)
        apiResponse.raise_for_status()
        apiResponseJson = apiResponse.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return apiResponseJson

def extractValidData(response) -> list[dict]:
    """
    Извлекает из JSON-ответа данные в виде списка словарей.

    Если ответ — список, возвращает его напрямую.\\
    Если в словаре присутствуют простые типы (str/int/float/bool), возвращает весь ответ, считая его уже необходимыми данными.
    Если ответ — словарь и отсутствуют простые типы, то возвращается список с самым большим количество элементов.
    
    В противном случае возвращает пустой список.

    Args:
        response (dict | list): JSON-ответ от API.

    Returns:
        list[dict]: Список элементов данных для дальнейшей обработки.
    """
    dataLists = []
    if isinstance(response, list):
        return response
    elif isinstance(response, dict):
        for value in response.values():
            if isinstance(value, list):
                dataLists.append(value)
            elif isinstance(value, (str, int, float, bool)):
                return [response]
    
    if dataLists:
        return max(dataLists, key=len)
    else:
        print("No supported data was found")
        return []

def constructFilename(url : str) -> str:
    """
    Формирует корректное имя файла на основе URL и текущей даты.
    Недопустимые символы отбрасываются.

    Args:
        url (str): Исходный URL.

    Returns:
        str: Безопасное имя файла.
    """
    date = datetime.date.today()
    return f"{'_'.join(filter(lambda x: all(c in allowedChars for c in x), url.split('/')[3:]))}_{date}.txt"

def itemToStr(item):
    """
    Преобразует элемент любого типа в строку для записи в таблицу.

    Простые типы (str, int, float, bool, None) конвертируются напрямую.
    Сложные типы заменяются их названием (например, 'list', 'dict').

    Args:
        item (Any): Исходное значение.

    Returns:
        str: Текстовое представление значения или его типа.
    """
    itemType = type(item)
    if isinstance(item, (str, int, float, bool)) or item is None:
        data = str(item)
    else:
        data = itemType.__name__
    return data

def prepareResponseForWrite(header, response : list[dict]) -> tuple[list[list[str]], list[int]]:
    """
    Подготавливает данные для табличной записи:
    - Преобразует все значения в строки.
    - Определяет ширину колонок для выравнивания.

    Args:
        header (list[str]): Заголовки (ключи) таблицы.
        response (list[dict]): Список строк данных.

    Returns:
        tuple[list[list[str]], list[int]]:
            - Список значений по колонкам.
            - Список ширин колонок.
    """
    columnsWidth = []
    columnsValues = []
    for column in header:
        columnValues = []
        for row in response:
            item = row[column]
            data = itemToStr(item)
            columnValues.append(data)

        columnsValues.append(columnValues)
        columnsWidth.append(max(len(column), max(map(len, columnValues), default=0)))
    return columnsValues, columnsWidth

def writeDataToTable(filename: str, header, values: list, widths: list) -> None:
    """
    Записывает данные в таблицу формата .txt в виде ASCII-таблицы.
    
    Файл записывается в созданной папке.
    
    Таблица включает заголовок, разделительную линию и строки данных.

    Args:
        filename (str): Имя файла
        header (list[str]): Заголовки колонок.
        values (list[list[str]]): Двумерный список значений по колонкам.
        widths (list[int]): Ширины каждой колонки.
    """

    filePath = f"{outputDirectory}\\{filename}"
    with open(filePath, "w", encoding="utf-8") as file:
        file.write("|" + " ".join(head.ljust(width) for head, width  in zip(header, widths)) + "|\n")
        file.write("|" + " ".join('-' * width for width in widths) + "|\n")
        for lineIndex in range(len(values[0])):
            file.write("|" + " ".join(column[lineIndex].ljust(width) for column, width in zip(values, widths)) + "|\n")
    print(f"Successfully recorded in {filePath}")

def main():
    """Точка входа программы"""
    session = requests.Session()
    session.verify = False
    
    requestURL = input("Enter GET request api url: ")
    if not os.path.isdir(outputDirectory):
        os.makedirs(outputDirectory)
    
    apiResponseJson = requestApiData(session, requestURL)
    response = extractValidData(apiResponseJson)
    if not response:
        exit(0)
    
    filename = constructFilename(requestURL)
    header = response[0].keys()
    columnsValues, columnsWidth = prepareResponseForWrite(header, response)
    writeDataToTable(filename, header, columnsValues, columnsWidth)

if __name__ == "__main__":
    main()