#! /usr/bin/python2.7

import sys
from urllib import urlopen
from os import path, makedirs, system
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BeautifulSoup import BeautifulSoup

from sqlalchemy_declarative import Manga, Chapter, Base
from media_handling import download_image, dump_images, generate_pdf


BASE_DIR = path.dirname(path.abspath(__file__))
MANGA_DIR = path.join(BASE_DIR, 'media')

GENRES = [
    'Action', 'Adventure', 'Comedy', 'Demons', 'Drama',
    'Ecchi', 'Fantasy', 'Gender Bender', 'Harem', 'Historical',
    'Horror', 'Josei', 'Magic', 'Martial Arts', 'Mature',
    'Mecha', 'Military', 'Mystery', 'One Shot', 'Psychological',
    'Romance', 'School Life', 'Sci-Fi', 'Seinen', 'Shoujo',
    'Shoujoai', 'Shounen', 'Shounenai', 'Slice of Life', 'Smut',
    'Sports', 'Super Power', 'Supernatural', 'Tragedy', 'Vampire',
    'Yaoi', 'Yuri'
]


def simple_format(manga):
    '''Converts the manga name to '''
    formatted = []

    for i, c in enumerate(manga):
        if c.isalnum():
            formatted.append(c.lower())

        else:
            formatted.append('-')

    return ''.join(formatted)


def manga_url(site, manga):
    return path.join(site, simple_format(manga))


class Max:
    source_site = 'http://mangareader.net'

    def __init__(self, db):
        # Initialize the db session
        engine = create_engine(db)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def find_manga(self, manga_name, forced=False):
        '''Checks if you have the information and chapter list of a given manga. If not, it fetches it.'''
        manga = self.session.query(Manga).filter(Manga.name == manga_name).first()

        if manga is not None and not forced:
            print 'Manga %s found in database.' % manga_name
            return manga

        else:
            src = urlopen(manga_url(site=self.source_site, manga=manga_name))
            soup = BeautifulSoup(src)

            # Get properties
            properties = soup.find('div', {'id': 'mangaproperties'}).table.findChildren('tr')
            get_property = lambda p: p.findChildren('td')[1].string

            # Name
            name = properties[0].findChildren('td')[1].h2.string

            # Year of release, status, author, artist
            others = []
            for p in properties[2:6]:
                data = get_property(p)
                others.append(data if data is not None else '')

            # Genres
            genres = [genre.string for genre in properties[7].findChildren('span', {'class': 'genretags'})]

            # Create and save a Manga instance
            manga = Manga()
            manga.name = name
            manga.key = simple_format(name)
            manga.year_of_release = others[0]
            manga.ongoing = True if others[1] == 'Ongoing' else False
            manga.author = others[2]
            manga.artist = others[3]

            genre_str = []
            for GENRE in GENRES:
                if GENRE in genres:
                    genre_str.append('1')
                else:
                    genre_str.append('0')
            manga.genres = ''.join(genre_str)

            self.session.add(manga)

            # Get chapter list
            previous_siblings = soup.find('div', {'id': 'chapterlist'}).findChildren('div', {'class': 'chico_manga'})
            raw_chapter_list = [previous_sibling.nextSibling.nextSibling.nextSibling[3:] for previous_sibling in previous_siblings]

            for i, c in enumerate(raw_chapter_list[:-1]):
                chapter = Chapter(manga=manga, name=c, number=i + 1)
                self.session.add(chapter)

            chapter = Chapter(manga=manga, name=raw_chapter_list[-1], number=len(raw_chapter_list), latest=True)
            self.session.add(chapter)

            self.session.commit()

            # Print statements
            print 'Successfully downloaded information and the chapter list for manga %s.' % manga.name
            return manga


    def find_chapters(self, manga_name, chapter_numbers, forced=False):
        '''Gets the urls of all the pages of a given chapter'''
        # Check if manga is in database, if not, download.
        manga = self.session.query(Manga).filter(Manga.name == manga_name).first()
        manga_uri = path.join(self.source_site, manga.key)
        directory = path.join(MANGA_DIR, manga.key)
        temp = path.join(MANGA_DIR, 'temp')

        # Check if directory exists, otherwise create it
        if not path.exists(directory):
            makedirs(directory)

        for chapter_number in chapter_numbers:
            chapter = self.session.query(Chapter).filter(Chapter.manga == manga).filter(Chapter.number == chapter_number).first()

            # Check if chapter is stored already.
            if chapter.stored and not forced:
                print '{0} {1} has already been downloaded.'.format(manga.name, chapter.number)

            else:
                dump_images(directory=temp)

                chapter_uri = path.join(manga_uri, str(chapter_number))
                pages = []

                src = urlopen(chapter_uri)
                soup = BeautifulSoup(src)

                # Get number of pages
                num_of_pages = int(soup.find('div', {'id': 'selectpage'}).select.nextSibling[4:])

                # Get page 1
                page_url = soup.find('div', {'id': 'imgholder'}).a.img['src']
                page = download_image(url=page_url, directory=temp, name=1)
                pages.append(page)
                print 'Page 1 of {0} {1} downloaded.'.format(manga.name, chapter.number)

                # Get other pages
                for i in xrange(2, num_of_pages + 1):
                    page_src = urlopen(path.join(chapter_uri, str(i)))
                    soup = BeautifulSoup(page_src)
                    page_url = soup.find('div', {'id': 'imgholder'}).a.img['src']
                    page = download_image(url=page_url, directory=temp, name=i)
                    pages.append(page)
                    print 'Page {0} of {1} {2} downloaded.'.format(i, manga.name, chapter.number)

                file_path = generate_pdf(images=pages, directory=directory, name=manga.key)

                chapter.stored = True
                chapter.path = file_path
                self.session.commit()

    def fetch(self, manga_name, chapter_number=None):
        manga = self.session.query(Manga).filter(Manga.name == manga_name).first()

        if manga is None:
            print 'Manga %s is not in database.' % manga_name

        else:
            print manga.name
            print 'Author: %s' % manga.author
            print 'Artist: %s' % manga.artist
            print 'Year of release: %s' % manga.year_of_release
            print 'Status: %s' % 'ongoing' if manga.ongoing else 'complete'
            sys.stdout.write('Genres: ')
            for i, j in enumerate(manga.genres):
                if j == '1':
                    sys.stdout.write('%s, ' % GENRES[i])
            sys.stdout.flush()

            if chapter_number is not None:
                chapter = self.session.query(Chapter).filter(Chapter.manga == manga).filter(Chapter.number == chapter_number).first()

                if chapter is None:
                    return 0

                else:
                    return chapter.path

            else:
                return 0


if __name__ == '__main__':
    my_max = Max('sqlite:///manga.db')
    argc = len(sys.argv)

    if argc <= 2:
        print 'Incorrect usage... Arguments required.'

    else:
        if sys.argv[1] == 'find' or sys.argv[1] == 'force':
            my_max.find_manga(sys.argv[2])
            args = sys.argv[3:]

            if argc >= 4:
                for arg in args:
                    if '-' in arg:
                        r = arg.split('-')
                        l = int(r[0])
                        u = int(r[1])
                        my_max.find_chapters(sys.argv[2], range(l, u + 1), forced=True if sys.argv[1] == 'force' else False)

                    else:
                        my_max.find_chapters(sys.argv[2], [int(arg)], forced=True if sys.argv[1] == 'force' else False)

        elif sys.argv[1] == 'fetch':

            if argc == 3:
                my_max.fetch(manga_name=sys.argv[2])

            elif argc == 4:
                p = my_max.fetch(manga_name=sys.argv[2], chapter_number=int(sys.argv[3]))
                if p != 0:
                    system('xdg-open %s' % p)

    print 'Done.'