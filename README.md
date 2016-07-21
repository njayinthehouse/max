# Manga Hound Max

A command-line utility for fetching and managing your manga.

**Setup**

Download the zip file, extract the contents, navigate into the directory, and run:

    sudo pip install -r requirements.txt
    python sqlalchemy_declarative.py


**Usage**

    python max.py find '<manga name>'
This code scrapes the details and chapter list of a manga from online and stores it in the database.

    python max.py find '<manga name>' '1'
This does the same as above as well as scrapes chapter 1 of that manga and stores it as a PDF file.

    python max.py find '<manga name>' '1-15'
This does the same as above for chapters 1-15.

    python max.py fetch '<manga name>'
This fetches the details of the manga given as a parameter from the database.

    python max.py fetch '<manga name>' '1'
This does the same as above as well as opens the PDF to chapter 1 using `xdg-open`.

**Requirements**

1. BeautifulSoup
2. Pillow
3. reportlab
4. requests
5. SQLAlchemy

The above can be installed by `pip install -r requirements.txt`.

In addition to these, `xdg-open` must also be installed on your computer.