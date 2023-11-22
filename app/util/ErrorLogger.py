def errorLog(service, index1, index2, errMessage):
    with open("log/SolvedErrorLog.txt", "w") as file:
        file.write(f"Index1: {index1}, Index2:{index2}, Error: {errMessage}\n")

# def errorLog(service, index1, index2, errMessage):
#     with open(service, "w") as file:
#         file.write(f"Index1: {index1}, Index2:{index2}, Error: {errMessage}\n")
