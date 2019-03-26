
def exit_if_errors(response, exit_code=1):
    if "errors" in response:
        status = code = detail = ""
        try:
            status = response["errors"][0]["status"]
        except:
            pass
        try:
            code = response["errors"][0]["code"]
        except:
            pass
        try:
            detail = response["errors"][0]["detail"]
        except:
            pass

        print("{} {} : {}".format(status, code, detail))
        print("Exitting due to error...")
        exit(exit_code)
