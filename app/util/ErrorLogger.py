def errorLog(service, index, errMessage):
    with open(service, "a") as file:
        file.write(f"Index: {index}, Error: {errMessage}\n")
