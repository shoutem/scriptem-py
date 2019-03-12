
def exit_if_errors(response, exit_code=1):
    if "errors" in response:
        print("{} {} : {}".format(
            response["errors"][0]["status"],
            response["errors"][0]["code"],
            response["errors"][0]["detail"]
        ))
        print("Exitting due to error...")
        exit(exit_code)
