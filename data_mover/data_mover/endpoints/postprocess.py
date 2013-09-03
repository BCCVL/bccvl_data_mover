import gzip


def gunzip(sourceFile, destFile):
    # gunzip the sourceFile to the destFile
    handle = gzip.open(sourceFile)
    with open(destFile, 'w') as out:
        for line in handle:
            out.write(line)

