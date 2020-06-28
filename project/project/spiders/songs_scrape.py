import scrapy
import json 
import re
from googletrans import Translator

class SongsScrape(scrapy.Spider):
    name = "songs"
    artist_name_translator = Translator()
    genere_name_translator = Translator()
    lyrics_by_name_translator = Translator()
    music_by_name_translator = Translator()
    movie_tranlator = Translator()
    objects = []
    song_name=""
    artist_name=""
    genere_name=""
    lyrics_by_name=""
    music_by_name=""
    lyrics=""
    allowed_domains= [
        'sinhalasongbook.com'
        ]

    
    def start_requests(self):
        urls = [
        ]
        for i in range(1,23):
            
            urls.append('https://sinhalasongbook.com/all-sinhala-song-lyrics-and-chords/?_page='+str(i))
            
        print(urls)
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            print(url)
  
    

    def parse(self, response):

        for quote in response.xpath('/html/body/div[1]/div[1]/div/main/article/div/div[3]/div[1]/div/div/div/h4/a/@href').getall():
            
            yield scrapy.Request(quote, callback=self.details_extractor)
            
            
    def details_extractor(self, response):
        
        self.song_name= response.xpath('/html/body/div[1]/div[1]/div/main/article/div[3]/h2/span/text()').get().strip().split("–")[-1].replace("|", "")
        self.artist_name=" , ".join(["" if artist == 'Unknown' else self.artist_name_translator.translate(artist,src='en', dest='si').text for artist in response.xpath('/html/body/div[1]/div[1]/div/main/article/div[3]/div[1]/div[2]/div/div/ul/li[1]/span/a/text()').getall()]).strip()
        self.genere_name=" , ".join(["" if genere == 'Unknown' else self.genere_name_translator.translate(genere,src='en', dest='si').text for genere in response.xpath('/html/body/div[1]/div[1]/div/main/article/div[3]/div[1]/div[2]/div/div/ul/li[2]/span/a/text()').getall()]).strip()
        self.lyrics_by_name=" , ".join(["" if lyrics_by == 'Unknown' else self.lyrics_by_name_translator.translate(lyrics_by,src='en', dest='si').text for lyrics_by in response.xpath('/html/body/div[1]/div[1]/div/main/article/div[3]/div[1]/div[3]/div/ul/li[1]/span/a/text()').getall()]).strip()
        self.music_by_name=" , ".join(["" if music_by == 'Unknown' else self.music_by_name_translator.translate(music_by,src='en', dest='si').text for music_by in response.xpath('/html/body/div[1]/div[1]/div/main/article/div[3]/div[1]/div[3]/div/ul/li[2]/span/a/text()').getall()]).strip()
        self.lyrics=  re.sub("[a-zA-Z0-9#\[\]|\/()\t{}∆— '=_+?*]",""," ".join( response.xpath('//pre/text()').getall()).replace("-", " ")).strip().replace("  ", "")
        if (self.song_name=="" or self.artist_name=="" or self.genere_name=="" or self.lyrics_by_name=="" or self.music_by_name=="" or self.lyrics==""):
            return
        
        details= {
            'name' : self.song_name ,
            'artist' : self.artist_name ,
            'genere' : self.genere_name ,         
            'lyrics by' :self.lyrics_by_name,
            'music by' : self.music_by_name,
            'movie' :" , ".join([self.movie_tranlator.translate(movie,src='en', dest='si').text for movie in response.xpath('/html/body/div[1]/div[1]/div/main/article/div[3]/div[1]/div[3]/div/ul/li[3]/span/a/text()').getall()]).strip(),
            'views' : response.xpath('/html/body/div[1]/div[1]/div/main/article/div[3]/div/text()').getall()[-1].split('-')[-1].split("Visits")[0].strip(),
            'shares' : response.xpath('/html/body/div[1]/div[1]/div/main/article/div[3]/div/div[4]/span/text()').get().strip(),
            'lyrics' : self.lyrics
              
            }
        self.objects.append(details)
        # with open("lyrics_objects.json", 'w', encoding="utf8") as outfile:
        #     json.dump( self.objects, outfile,indent = 4,ensure_ascii=False)
        
    def closed(self, reason):
        
        with open("lyrics_objects.json", 'w', encoding="utf8") as outfile:
           json.dump(self.objects, outfile,indent = 4,ensure_ascii=False)
           

        
        
