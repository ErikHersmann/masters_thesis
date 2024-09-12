import os.path

def write_output_without_overwrite(data: str):
    appendix = 0
    fname_base = "output/jobset_"
    while True:
        cfname = fname_base + str(appendix) + ".json"
        if os.path.isfile(cfname):
            appendix += 1
            continue
        else:
            with open(cfname, "a") as f:
                f.write(data)
            break




