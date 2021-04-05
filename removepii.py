# Author: Porter Zach
# Python 3.9

import argparse
import nltk
import re
import os
import pathlib

def extract(filePath):
    """Extracts the textual information from a file.

    Args:
        filePath (str): The path to the file to extract text from.

    Raises:
        ValueError: If the information could not be extracted due to unsupported file type.

    Returns:
        str: The text in the provided file.
    """
    # get the file extension
    ext = pathlib.Path(filePath).suffix

    # extract all data from pure text files
    if ext == ".txt" or ext == ".md":
        text = None
        with open(filePath) as file:
            text = file.read()
        return text

    # get the text from PDFs
    if ext == ".pdf":
        from pdfminer.high_level import extract_text
        return extract_text(filePath)

    # get the text minus tags from HTML files
    if ext == ".html" or ext == ".htm":
        from bs4 import BeautifulSoup
        with open(filePath) as file:
            soup = BeautifulSoup(file, "html.parser")
        return soup.get_text()

    raise ValueError(f"Text from file {filePath} could not be extracted. Supported types are TXT, PDF, HTML.")

def getNE(text, piiNE):
    """Gets the named entities classified as PII in the text.

    Args:
        text (str): The text to analyze.
        piiNE (list): The types of named entities classified as PII that should be removed. Options: PERSON, ORGANIZATION, GPE, LOCATIOn.

    Returns:
        set: The set of strings holding named entity PII.
    """
    # search for NLTK required data in this directory so the user doesn't need to download it separately
    nltk.data.path.append(os.getcwd())
    # gets all of the named entities in the text
    ne = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(text)))
    pii = []

    # checks if a subtree contains PII (i.e. it should be removed)
    def filterPII(x):
        return x.label() in piiNE

    # loops through all subtrees with a PII label
    for sub in ne.subtrees(filter = filterPII):
        # gets the PII's full text string from the subtree's leaves
        # ex: [('Google', 'NNP'), ('Science', 'NNP'), ('Fair', 'NNP')] -> Google Science Fair
        piiStr = " ".join(pair[0] for pair in sub.leaves())
        # adds the PII string to the list
        if piiStr not in pii:
            pii.append(piiStr)
    
    # converts to a set before returning to remove duplicates
    return set(pii)

def getIDInfo(text, types):
    """Gets the ID info classified as PII in the text.

    Args:
        text (str): The text to analyze.
        types (list): The types of ID info classified as PII that should be removed. Options: EMAIL, PHONE, SSN

    Returns:
        set: The set of strings holding ID info PII.
    """
    # gets whether each ID info type should be removed.
    phone = "PHONE" in types
    email = "EMAIL" in types
    ssn = "SSN" in types

    # return an empty set if we're not looking for any ID info PII
    if not(phone or email or ssn):
        return set([])

    # initialize the phone number regex
    if phone: phoneRegex = re.compile(r'''(
        (\d{3}|\(\d{3}\))? # area code
        (\s|-|\.)? # separator
        (\d{3}) # first 3 digits
        (\s|-|\.) # separator
        (\d{4}) # last 4 digits
        (\s*(ext|x|ext.)\s*(\d{2,5}))? # optional extension
        )''', re.VERBOSE)

    # initialize the email address regex
    if email: emailRegex = re.compile(r'''(
        [a-zA-Z0-9._%+-] + # username
        @ # @symbol
        [a-zA-Z0-9.-] + # domain
        (\.[a-zA-Z]{2,4}) # .something
        )''', re.VERBOSE)

    # initialize the social security number regex
    if ssn: ssnRegex = re.compile(r'''(
        (?!666|000|9\d{2})\d{3} # SSN can't begin with 666, 000 or anything between 900-999
        - # explicit dash (separating Area and Group numbers)
        (?!00)\d{2} # don't allow the Group Number to be "00"
        - # another dash (separating Group and Serial numbers)
        (?!0{4})\d{4} # don't allow last four digits to be "0000"
        )''', re.VERBOSE)

    pii = []

    # utility method for getting PII matches
    def getMatches(pattern, t):
        # for each match, return the match itself if it is a string or the first member of a tuple match
        # this is because matches are sometimes tuples of multiple groups, like a phone number match being:
        # ("800-999-2222", "800", "-", "999", "-", "2222")
        # However, sometimes the matches are just strings (no groups), so accessing the element at [0] would get the first char, which is not desirable.
        return [(match if type(match) is str else match[0]) for match in pattern.findall(t)]

    # adds the found phone #s, emails, and SSNs to the PII list
    if phone: pii += getMatches(phoneRegex, text)
    if email: pii += getMatches(emailRegex, text)
    if ssn: pii += getMatches(ssnRegex, text)

    # converts to a set before returning to remove duplicates
    return set(pii)

def writeFile(text, path):
    """Writes text to the file path.

    Args:
        text (str): The text to write.
        path (str): The path to write the file to.
    """
    with open(path, "w") as file:
        file.write(text)

def cleanString(text, 
        verbose = False, 
        piiNE = ["PERSON", "ORGANIZATION", "GPE", "LOCATION"], 
        piiNums = ["PHONE", "EMAIL", "SSN"]):
    """Cleans a string of PII.

    Args:
        text (str): The text to clean.
        verbose (bool, optional): Whether status updates should be printed to the console. Defaults to False.
        piiNE (list, optional): The types of named entity PII to remove. Defaults to all types: ["PERSON", "ORGANIZATION", "GPE", "LOCATION"].
        piiNums (list, optional): The types of ID info PII to remove. Defaults to all types: ["PHONE", "EMAIL", "SSN"].

    Returns:
        str: The cleaned text string with PII replaced with XXXXX values.
    """
    if verbose: print("Cleaning text: getting named entities and identifiable information...")
    # combines the NE and ID info PII string sets
    piiSet = set.union(getNE(text, piiNE), getIDInfo(text, piiNums))
    if verbose: print(str(len(piiSet)) + " PII strings found.")

    if verbose: print("Removing PII.")
    # replaces PII with XXXXX values
    cleaned = text
    for pii in piiSet:
        cleaned = cleaned.replace(pii, "XXXXX")
    
    # return the cleaned text string
    return cleaned

def cleanFile(filePath, outputPath, 
        verbose = False,
        piiNE = ["PERSON", "ORGANIZATION", "GPE", "LOCATION"], 
        piiNums = ["PHONE", "EMAIL", "SSN"]):
    """Reads a file with PII and saves a copy of that file with PII removed.

    Args:
        filePath (str): The path to the file with PII.
        outputPath (str): The path to the cleaned file to be saved.
        verbose (bool, optional): Whether status updates should be printed to the console. Defaults to False.
        piiNE (list, optional): The types of named entity PII to remove. Defaults to all types: ["PERSON", "ORGANIZATION", "GPE", "LOCATION"].
        piiNums (list, optional): The types of ID info PII to remove. Defaults to all types: ["PHONE", "EMAIL", "SSN"].
    """
    if verbose: print("Extracting text from " + filePath + "...")
    # gets the file's text
    text = extract(filePath)
    if verbose: print("Text extracted.")

    # gets the text without PII
    cleaned = cleanString(text, verbose, piiNE, piiNums)
    
    if verbose: print("Writing clean text to " + outputPath + ".")
    # write the cleaned text to the output file
    writeFile(cleaned, outputPath)

# if this file is being executed on the command line, parse arguments and process the user's file or text
if __name__ == "__main__":
    parser = argparse.ArgumentParser("Removes personally identifiable information (PII) like names and phone numbers from text strings and files.")

    parser.add_argument("-f", nargs=2, dest="path", default=[], metavar=("inputPath","outputPath"), help="the file to remove PII from and the clean output file path")
    parser.add_argument("-s", dest="text", default=None, help="input a text string to clean")

    args = parser.parse_args()

    # cleans the user's provided file
    if len(args.path) == 2:
        cleanFile(args.path[0], args.path[1], verbose=True)
    # cleans the user's provided text
    elif args.text is not None:
        s = cleanString(args.text, verbose=True)
        print("Text with PII removed:\n" + s)
    else:
        print("No action specified.")