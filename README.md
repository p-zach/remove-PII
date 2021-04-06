# PII-Scissors

Automatically removes personally identifiable information (PII) from text files and strings. Has the capability to remove names of people and organizations; names of geo-political entities (GPEs) and locations; and phone numbers, email addresses, and social security numbers. Only the PII is removed; the bulk of the sentence and the majority of the relevant information is retained.

## Samples

While working as an intern at Apple, Jonathan McJonathan was part of the software development team. His email address is jonj8653@radmail.org and you can call him at 800-123-4567.

PII Removed: While working as an intern at XXXXX, XXXXX was part of the software development team. His email address is XXXXX and you can call him at XXXXX.

Although Jonathan lived in California, his nephew Ron lived in Wisconsin. Both of them had aspirations for bigger things, so they started a company called Ron & Jon's that sold beef. Here's a social security number example: 123-45-0987.

PII Removed: Although XXXXX lived in XXXXX, his nephew XXXXX lived in XXXXX. Both of them had aspirations for bigger things, so they started a company called XXXXX & XXXXX's that sold beef. Here's a social security number example: XXXXX.

## Usage
Command line:
```
usage: Removes personally identifiable information (PII) like names and phone numbers 
       from text strings and files.
       [-h] [-f inputPath outputPath] [-s TEXT]

optional arguments:
  -h, --help            show this help message and exit
  -f inputPath outputPath
                        the file to remove PII from and the clean output file path
  -s TEXT               input a text string to clean
```
Code:
```
import cleanString from removepii

text = """My name is Robert. I work at Google. My phone number is 800-100-2222
and my email address is robbie@gmail.com."""

print(cleanString(text)) 
# output: "My name is XXXXX. I work at XXXXX. My phone number is XXXXX and my email address is XXXXX."

# piiNE is a list parameter with a default value of ["PERSON", "ORGANIZATION", "GPE", "LOCATION"]. 
# The program will remove any named entities that fit into the categories in the list.
# piiNums is a list parameter with a default value of ["PHONE", "EMAIL", "SSN"]. Like piiNE, any 
# information in the text that falls into a category in the list will be removed.

print(cleanString(text, piiNE=["PERSON"], piiNums=["PHONE"]) 
# output: "My name is XXXXX. I work at Google. My phone number is XXXXX and my email address is robbie@gmail.com."

import cleanFile from removepii

# reads file "pii.pdf" and writes the cleaned text to "clean.txt"
# piiNE and piiNums arguments are accepted here as well.
cleanFile("pii.pdf", "clean.txt")
```

## Requirements

pip packages:

`nltk`

`pdfminer.six` if PDF reading is desired

`bs4` if HTML reading is desired