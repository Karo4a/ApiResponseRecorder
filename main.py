import requests, datetime, os, urllib3, string

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
outputDirectory = "output"
allowedChars = string.ascii_letters + string.digits + "-"

def process_response(response) -> list[dict]:
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
        return sorted(dataLists)[0]
    else:
        print("No supported data was found")
        return []

if __name__ == "__main__":
    session = requests.Session()
    session.verify = False
    
    requestURL = input("Enter request api url: ")
    if not os.path.isdir(outputDirectory):
        os.makedirs(outputDirectory)
    
    date = datetime.date.today()
    try:
        apiResponse : requests.Response = session.get(requestURL)
        apiResponse.raise_for_status()
        apiResponseJson = apiResponse.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    response = process_response(apiResponseJson)
    if not response:
        exit(0)

    filename = f"{'_'.join(filter(lambda x: all(c in allowedChars for c in x), requestURL.split('/')[3:]))}_{date}.txt"
    filePath = f"{outputDirectory}\{filename}"
    with open(filePath, "w", encoding="utf-8") as file:
        header = response[0].keys()
        columnsWidth = []
        columnsValues = []
        for column in header:
            columnValues = []
            for row in response:
                item = row[column]
                itemType = type(item)
                if isinstance(item, (str, int, float, bool)) or item is None:
                    data = str(item)
                else:
                    data = itemType.__name__
                columnValues.append(data)

            columnsValues.append(columnValues)
            columnsWidth.append(max(len(column), max(map(len, columnValues), default=0)))

        file.write("|" + " ".join(head.ljust(width) for head, width  in zip(header, columnsWidth)) + "|\n")
        file.write("|" + " ".join('-'*width for width in columnsWidth) + "|\n")
        for lineIndex in range(len(response)):
            file.write("|" + " ".join(column[lineIndex].ljust(width) for column, width in zip(columnsValues, columnsWidth)) + "|\n")
    print(f"Successfully recorded in {filePath}")